Use case: infographic-diagram
Asset type: TaskBeacon task flow diagram
Primary request: Create a clean, publication-ready task flow diagram as a timeline collection for the behavioral task described below.

Task: Retrieval-Induced Forgetting
Construct: retrieval-induced forgetting / episodic retrieval inhibition
Rows/conditions:
- Session order: four participant-visible stages in their exact order.
- Study item: category-exemplar study presentation.
- Rp+ retrieval practice: category and first-character cue with typed recall, repeated for three rounds.
- Arithmetic distractor: odd/even judgment with F/J response.
- Final cued recall: identical visible test format for Rp+, Rp-, and Nrp items; Rp-/Nrp are tested before Rp+.

Timeline phases:
- Session order: Study (48 items; `类别：水果` and `苹果`) -> Retrieval practice (36 trials; three rounds; category plus first-character cue) -> Arithmetic distractor (120 trials; 20 min total; F/J parity choice) -> Final test (48 items; Rp-/Nrp before Rp+)
- Study item: Category-exemplar (`类别：水果` above `苹果`; 5 s; no response) -> Next pair (`类别：动物` above `老虎`; 5 s; no response)
- Rp+ retrieval practice: Cue (`提取练习`; `类别：颜色`; `词语线索：红＿＿`; 10 s max) -> Type (`红色` in response box; Enter) -> Repeat (three rounds total)
- Arithmetic distractor: Problem (`7 + 4 = 11`; 10 s fixed) -> Choice (`F 奇数`; `J 偶数`) -> Next problem (120 trials; 20 min total)
- Final cued recall: Cue (`最终回忆`; `类别：水果`; `词语线索：苹＿＿`; 7 s max) -> Type (`苹果` in response box; Enter) -> Continue (48 items; Rp-/Nrp before Rp+)

Visual requirements:
- White background, landscape orientation, crisp dark text, restrained condition accent colors.
- One horizontal row per condition or representative trial type.
- Each row contains 3-7 participant-screen snapshots connected by a subtle arrow.
- Each screen snapshot shows the visible stimulus or feedback, not internal variable names.
- Use gray participant-screen boxes, thin black arrows, consistent row spacing, and subtle row separators.
- Place timing labels under each screen in compact text.
- Place condition labels at the left of each row.
- Use short labels only; avoid paragraphs inside the image.
- Make all text legible at normal document preview size.
- Leave a clean blank header band across the top 15-18% of the image. This band is reserved for a fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup that will be added after generation.

Accuracy constraints:
- Do not invent phases, stimuli, condition names, keys, rewards, or timings.
- Do not add people, lab equipment, decorative scenes, logos, or unrelated icons.
- Do not draw the task title, construct subtitle, any logo, watermark, brand mark, or `TaskBeacon` text inside the generated image.
- Draw only the timeline content below the blank header band.
- If a detail is unknown, omit it rather than guessing.
- Preserve these exact terms where used: Study, Retrieval practice, Arithmetic distractor, Final test, Rp+, Rp-, Nrp, 5 s, 10 s max, 20 min total, 7 s max, F, J, Enter, 类别：水果, 苹果, 类别：动物, 老虎, 提取练习, 类别：颜色, 词语线索：红＿＿, 红色, F 奇数, J 偶数, 最终回忆, 词语线索：苹＿＿

Style:
TaskBeacon scientific infographic style: clean vector-like raster image, organized spacing, gray screen boxes, restrained color accents, and a blank header-safe area.

Revision request:
Keep the same task and overall four-row timeline-collection structure, proportions, colors, and readable Chinese typography.
Fix only these issues:
1. Remove the unsupported `+` fixation screen from the Study row. Show consecutive category-exemplar pairs only, followed by a compact repeat/next-pair indicator.
2. Remove every unsupported `已记录`, checkmark, success, or feedback screen. Retrieval practice is cue -> typed response + Enter -> repeat ×3. Arithmetic distractor is one combined equation/F/J response screen -> next problem. Final test is cue -> typed response + Enter -> continue.
Do not add new conditions, phases, stimuli, people, devices, logos, or decorative scenery.
Leave a clean blank top header band; the fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup will be added after generation.
Preserve the exact condition labels and timing labels from the prompt.
