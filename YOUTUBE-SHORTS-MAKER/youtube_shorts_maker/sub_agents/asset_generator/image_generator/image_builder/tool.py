import base64
from google.genai import types
from openai import OpenAI
from google.adk.tools.tool_context import ToolContext

client = OpenAI


async def generate_images(tool_context: ToolContext):

    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")

    existing_artifacts = await tool_context.list_artifacts()

    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")

        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt[:100],
                    "filename": filename,
                }
            )
            continue

        image = client.images.generate(
            model="openai/gpt-image-1",
            prompt=enhanced_prompt,
            n=1,
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )

        image_bytes = base64.b64encode(image.data[0].binary).decode("utf-8")
        artifact = types.Blob(
            mime_type="image/jpeg",
            data=image_bytes,
        )
        await tool_context.save_artifact(
            filename, 
            artifact
            )
        generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt[:100],
                    "filename": filename,
                }
            )
    return {
        "total_images": len(generated_images),
        "status": "success",
        "generated_images": generated_images,
    }