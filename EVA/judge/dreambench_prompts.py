"""DreamBench++ official CP/PF task prompts and summary-planning prefills."""

OFFICIAL_CP_TASK = """### Task Definition
You will be provided with an image generated based on reference image.
As an experienced evaluator, your task is to evaluate the semantic consistency between the subject of the generated image and the reference image, according to the scoring criteria.

### Scoring Criteria
It is often compared whether two subjects are consistent based on four basic visual features:
1. Shape: Evaluate whether the main body outline, structure, and proportions of the generated image match those of the reference image. This includes the geometric shape of the main body, clarity of edges, relative sizes, and spatial relationships between various parts composing the main body.
2. Color: Comparing the accuracy and consistency of the main colors generated in the image with those of the reference image. This includes saturation, hue, brightness, and whether the distribution of colors is similar to that of the subject in the reference image.
3. Texture: Focus on the local parts of the RGB image, whether the generated image effectively captures fine details without appearing blurry, and whether it possesses the required realism, clarity, and aesthetic appeal. Please note that unless specifically mentioned in the text prompt, excessive abstraction and formalization of texture are not necessary.
4. Facial Features: If the evaluation is of a person or animal, facial features will greatly affect the judgment of image consistency, and you also need to focus on judging whether the facial area looks very similar visually.

### Scoring Range
You need to give a specific integer score based on the comprehensive performance of the visual features above, ranging from 0 to 4:
- Very Poor (0): No resemblance. The generated image's subject has no relation to the reference.
- Poor (1): Minimal resemblance. The subject falls within the same broad category but differs significantly.
- Fair (2): Moderate resemblance. The subject shows likeness to the reference with notable variances.
- Good (3): Strong resemblance. The subject closely matches the reference with only minor discrepancies.
- Excellent (4): Near-identical. The subject of the generated image is virtually indistinguishable from the reference.

### Input format
Every time you will receive two images, the first image is a reference image, and the second image is the generated image.

Please carefully review each image of the subject.

### Output Format
Score: [Your Score]

You must adhere to the specified output format, which means that only the scores need to be output, excluding your analysis process."""

OFFICIAL_CP_PLAN = """Yes, I understand the task. It involves evaluating the semantic consistency between a reference image and a generated image based on specific criteria. The evaluation focuses on four main aspects: shape, color, texture, and facial features (if applicable). The goal is to determine how closely the generated image matches the reference image in terms of these aspects. The evaluation should result in a specific score ranging from 0 (no resemblance) to 4 (near-identical resemblance).

To evaluate the images, I plan to follow these steps:

1. **Shape**: Assess if the main body outline, structure, and proportions of the generated image are consistent with the reference image. This includes looking at the geometric shape, clarity of edges, relative sizes, and spatial relationships between various parts.
2. **Color**: Compare the main colors in terms of accuracy and consistency, including saturation, hue, brightness, and the distribution of colors.
3. **Texture**: Examine the details in the local parts of the image to see if the generated image captures fine details without appearing blurry and maintains realism, clarity, and aesthetic appeal.
4. **Facial Features**: If the subject includes a person or animal, closely compare facial features to judge visual similarity.

After analyzing these aspects, I will assign a score based on the overall performance of the generated image in relation to the reference image. The score will reflect how similar the generated image is to the reference image, strictly adhering to the evaluation criteria provided.

My output format should be Score: [0-4], and I don't need to write out the specific analysis process.

Please provide me with the samples I need to evaluate."""

OFFICIAL_PF_TASK = """### Task Definition
You will be provided with an image and text prompt.
As an experienced evaluator, your task is to evaluate the semantic consistency between image and text prompt, according to the scoring criteria.

### Scoring Criteria
When assessing the semantic consistency between an image and its accompanying text, it is crucial to consider how well the visual content of the image aligns with the textual description. This evaluation can be based on several key aspects:
1. Relevance: Determine if the elements and subjects presented in the image directly relate to the core topics and concepts mentioned in the text. The image should reflect the main ideas or narratives described in the text.
2. Accuracy: Examine the image for the presence and correctness of specific details mentioned in the text. This includes the depiction of particular objects, settings, actions, or characteristics that the text describes.
3. Completeness: Evaluate whether the image captures all the critical elements of the text. The image should not omit significant details that are necessary for the full understanding of the text's message.
4. Context: Consider the context in which the text places the subject and whether the image accurately represents this setting. This includes the portrayal of the appropriate environment, interactions, and background elements that align with the text.

### Scoring Range
Based on these criteria, a specific integer score from 0 to 4 can be assigned to determine the level of semantic consistency:
- Very Poor (0): No correlation. The image does not reflect any of the key points or details of the text.
- Poor (1): Weak correlation. The image addresses the text in a very general sense but misses most details and nuances.
- Fair (2): Moderate correlation. The image represents the text to an extent but lacks several important details or contains some inaccuracies.
- Good (3): Strong correlation. The image accurately depicts most of the information from the text with only minor omissions or inaccuracies.
- Excellent (4): Near-perfect correlation. The image captures the text's content with high precision and detail, leaving out no significant information.

### Input format
Every time you will receive a text prompt and an image.

Please carefully review image and text prompt. Before giving a score, please provide a brief analysis of the above evaluation criteria, which should be very concise and accurate.

### Output Format
Analysis: [Your analysis]
Score: [Your Score]"""

OFFICIAL_PF_PLAN = """Yes, I understand the task. It involves evaluating the semantic consistency between an image and its accompanying text prompt based on four key criteria: relevance, accuracy, completeness, and context. The goal is to determine how well the visual content of the image aligns with the textual description, considering both direct and nuanced connections. The evaluation will result in a score ranging from 0 to 4, reflecting the level of consistency between the image and text, where 0 indicates no correlation and 4 indicates a near-perfect correlation.

To evaluate the semantic consistency, I will:

1. **Relevance**: Check if the subjects and elements in the image are directly related to the main topics and concepts mentioned in the text.
2. **Accuracy**: Look for the presence of specific details in the image that the text mentions, ensuring these details are depicted correctly.
3. **Completeness**: Assess whether the image captures all critical elements and details mentioned in the text, ensuring no significant part of the text's message is missing.
4. **Context**: Examine if the image accurately represents the setting and context described in the text, including appropriate environments, interactions, and background elements.

After considering these criteria, I will provide a concise analysis and assign a score that reflects the overall semantic consistency between the image and text. The score will reflect how similar the generated image is to the text prompt, strictly adhering to the evaluation criteria provided.

Please provide me with the samples I need to evaluate."""
