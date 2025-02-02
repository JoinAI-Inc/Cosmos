# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess

import gradio as gr

# Define aspect ratios with corresponding width and height
aspect_ratios = [
    {"label": "1:1", "width": 960, "height": 960},
    {"label": "4:3", "width": 960, "height": 704},
    {"label": "3:4", "width": 704, "height": 960},
    {"label": "16:9", "width": 1280, "height": 704},
    {"label": "9:16", "width": 704, "height": 1280},
]


# Function to run text2world.py
def generate_text2world(
    prompt,
    model_size,
    offload_options,
    seed,
    negative_prompt,
    num_steps,
    guidance,
    num_video_frames,
    aspect_ratio,
    fps,
    disable_prompt_upsampler,
):
    # Get width and height based on aspect ratio
    selected_ar = next(ar for ar in aspect_ratios if ar["label"] == aspect_ratio)
    width = selected_ar["width"]
    height = selected_ar["height"]

    offload_prompt_upsampler = "Offload Prompt Upsampler" in offload_options
    offload_guardrail_models = "Offload Guardrail Models" in offload_options
    offload_tokenizer = "Offload Tokenizer" in offload_options
    offload_diffusion_transformer = "Offload Diffusion Transformer" in offload_options
    offload_text_encoder_model = "Offload Text Encoder Model" in offload_options

    args = [
        "PYTHONPATH=$(pwd) python cosmos1/models/diffusion/inference/text2world.py",
        "--checkpoint_dir checkpoints",
        f"--diffusion_transformer_dir Cosmos-1.0-Diffusion-{model_size}-Text2World",
        f'--prompt "{prompt}"',
        "--video_save_name output_text2world",
        f"--seed {seed}",
        f'--negative_prompt "{negative_prompt}"',
        f"--num_steps {num_steps}",
        f"--guidance {guidance}",
        f"--num_video_frames {num_video_frames}",
        f"--height {height}",
        f"--width {width}",
        f"--fps {fps}",
    ]

    if disable_prompt_upsampler:
        args.append("--disable_prompt_upsampler")
        if prompt:
            args.extend([f'--prompt "{prompt}"'])
        else:
            raise ValueError("Prompt is required when prompt upsampler is disabled.")

    if offload_prompt_upsampler:
        args.append("--offload_prompt_upsampler")
    if offload_guardrail_models:
        args.append("--offload_guardrail_models")
    if offload_tokenizer:
        args.append("--offload_tokenizer")
    if offload_diffusion_transformer:
        args.append("--offload_diffusion_transformer")
    if offload_text_encoder_model:
        args.append("--offload_text_encoder_model")

    command = " ".join(args)
    subprocess.run(command, shell=True)

    video_path = "outputs/output_text2world.mp4"
    return video_path


# Function to run video2world.py
def generate_video2world(
    input_file,
    model_size,
    num_input_frames,
    prompt,
    disable_prompt_upsampler,
    offload_options,
    seed,
    negative_prompt,
    num_steps,
    guidance,
    num_video_frames,
    aspect_ratio,
    fps,
):
    # Get width and height based on aspect ratio
    selected_ar = next(ar for ar in aspect_ratios if ar["label"] == aspect_ratio)
    width = selected_ar["width"]
    height = selected_ar["height"]

    offload_prompt_upsampler = "Offload Prompt Upsampler" in offload_options
    offload_guardrail_models = "Offload Guardrail Models" in offload_options
    offload_tokenizer = "Offload Tokenizer" in offload_options
    offload_diffusion_transformer = "Offload Diffusion Transformer" in offload_options
    offload_text_encoder_model = "Offload Text Encoder Model" in offload_options

    args = [
        "PYTHONPATH=$(pwd) python cosmos1/models/diffusion/inference/video2world.py",
        "--checkpoint_dir checkpoints",
        f"--diffusion_transformer_dir Cosmos-1.0-Diffusion-{model_size}-Video2World",
        f"--input_image_or_video_path {input_file}",
        "--video_save_name output_video2world",
        f"--seed {seed}",
        f"--num_input_frames {num_input_frames}",
        f'--negative_prompt "{negative_prompt}"',
        f"--num_steps {num_steps}",
        f"--guidance {guidance}",
        f"--num_video_frames {num_video_frames}",
        f"--height {height}",
        f"--width {width}",
        f"--fps {fps}",
    ]

    if disable_prompt_upsampler:
        args.append("--disable_prompt_upsampler")
        if prompt:
            args.extend([f'--prompt "{prompt}"'])
        else:
            raise ValueError("Prompt is required when prompt upsampler is disabled.")

    if offload_prompt_upsampler:
        args.append("--offload_prompt_upsampler")
    if offload_guardrail_models:
        args.append("--offload_guardrail_models")
    if offload_tokenizer:
        args.append("--offload_tokenizer")
    if offload_diffusion_transformer:
        args.append("--offload_diffusion_transformer")
    if offload_text_encoder_model:
        args.append("--offload_text_encoder_model")

    command = " ".join(args)
    subprocess.run(command, shell=True)

    video_path = "outputs/output_video2world.mp4"
    return video_path


# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# JoinAI Cosmos diffusion-based world foundation models demo")

    with gr.Tab("Text2World"):
        text_prompt = gr.Textbox(label="文本提示", lines=5)
        model_size_text = gr.Radio(["7B", "14B"], label="模型选择", value="7B")
        offload_options_text = gr.CheckboxGroup(
            [
                "Offload Prompt Upsampler",
                "Offload Guardrail Models",
                "Offload Tokenizer",
                "Offload Diffusion Transformer",
                "Offload Text Encoder Model",
            ],
            label="卸载选项(48G显存以下，记得全部勾选)",
        )
        seed_text = gr.Number(label="随机种子", value=1)
        disable_prompt_upsampler_text = gr.Checkbox(label="禁用提示自动优化")
        negative_prompt_text = gr.Textbox(
            label="负面提示词",
            value="""The video captures a series of frames showing ugly scenes, static with no motion, motion blur, over-saturation, shaky footage, low resolution, grainy texture, pixelated images, poorly lit areas, underexposed and overexposed scenes, poor color balance, washed out colors, choppy sequences, jerky movements, low frame rate, artifacting, color banding, unnatural transitions, outdated special effects, fake elements, unconvincing visuals, poorly edited content, jump cuts, visual noise, and flickering. Overall, the video is of poor quality.""",
            lines=5,
        )
        num_steps_text = gr.Number(label="步数", value=35)
        guidance_text = gr.Number(label="引导系数", value=7)
        num_video_frames_text = gr.Number(label="视频帧数", value=121)
        aspect_ratio_text = gr.Dropdown(
            choices=[ar["label"] for ar in aspect_ratios], label="宽高比", value="16:9"
        )
        fps_text = gr.Number(label="帧率", value=24, info="支持12到40之间的帧率")
        generate_button_text = gr.Button("生成视频")
        output_video_text = gr.Video(label="生成的视频")

        generate_button_text.click(
            generate_text2world,
            inputs=[
                text_prompt,
                model_size_text,
                offload_options_text,
                seed_text,
                negative_prompt_text,
                num_steps_text,
                guidance_text,
                num_video_frames_text,
                aspect_ratio_text,
                fps_text,
                disable_prompt_upsampler_text,
            ],
            outputs=output_video_text,
        )

    with gr.Tab("Video2World"):
        input_file = gr.File(label="输入图像/视频")
        model_size_video = gr.Radio(["7B", "14B"], label="模型选择", value="7B")
        num_input_frames = gr.Slider(1, 9, step=1, label="输入帧数", value=1)
        text_prompt_video = gr.Textbox(label="文本提示（可选）", lines=5)
        disable_prompt_upsampler_video = gr.Checkbox(label="禁用提示自动优化")
        offload_options_video = gr.CheckboxGroup(
            [
                "Offload Prompt Upsampler",
                "Offload Guardrail Models",
                "Offload Tokenizer",
                "Offload Diffusion Transformer",
                "Offload Text Encoder Model",
            ],
            label="卸载选项(48G显存以下，记得全部勾选)",
        )
        seed_video = gr.Number(label="随机种子", value=1)
        negative_prompt_video = gr.Textbox(
            label="负面提示词",
            value="""The video captures a series of frames showing ugly scenes, static with no motion, motion blur, over-saturation, shaky footage, low resolution, grainy texture, pixelated images, poorly lit areas, underexposed and overexposed scenes, poor color balance, washed out colors, choppy sequences, jerky movements, low frame rate, artifacting, color banding, unnatural transitions, outdated special effects, fake elements, unconvincing visuals, poorly edited content, jump cuts, visual noise, and flickering. Overall, the video is of poor quality.""",
            lines=5,
        )
        num_steps_video = gr.Number(label="步数", value=35)
        guidance_video = gr.Number(label="引导系数", value=7)
        num_video_frames_video = gr.Number(label="视频帧数", value=121)
        aspect_ratio_video = gr.Dropdown(
            choices=[ar["label"] for ar in aspect_ratios], label="宽高比", value="16:9"
        )
        fps_video = gr.Number(label="帧率", value=24, info="支持12到40之间的帧率")
        generate_button_video = gr.Button("生成视频")
        output_video_video = gr.Video(label="生成的视频")

        generate_button_video.click(
            generate_video2world,
            inputs=[
                input_file,
                model_size_video,
                num_input_frames,
                text_prompt_video,
                disable_prompt_upsampler_video,
                offload_options_video,
                seed_video,
                negative_prompt_video,
                num_steps_video,
                guidance_video,
                num_video_frames_video,
                aspect_ratio_video,
                fps_video,
            ],
            outputs=output_video_video,
        )
if __name__ == "__main__":
    demo.launch(share=True)