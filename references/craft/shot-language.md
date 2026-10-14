本卡用于单图机位与多图观看关系。静态图片只写当前机位、焦点及动作时刻，不将连续运镜、声音或剪辑指令当成单图执行要求。

# Shot language

Read only for camera position, framing, relation coverage or image-prompt composition. Keep dramatic purpose first; camera exists to reveal it.

同时遵循 [动作范围、首尾状态与剪辑衔接](action-endpoint-continuity.md)：分开描述主体动作与机位变化，核对上一镜后果和下一镜入场状态；剪辑成片可读性与原始生成遵守度分别判断。

## Intent versus execution

Write both. Never mix them into one adjective pile.

| Field | Holds | Example |
|-------|-------|---------|
| Camera intent | why this move exists | tighten as the lie starts to fail |
| Camera execution | type, angle, distance, speed, focus | start 0 deg 2.0m, push to 0 deg 1.0m in 3s, 50mm to 85mm |

If intent and execution conflict, execution wins for numbers; intent still explains the cut.

## Clock azimuth

Describe camera relative to the subject:

| Label | Deg | Meaning |
|-------|-----|---------|
| front | 0 | facing the subject |
| right | 90 | subject's right |
| back | 180 | behind |
| left | 270 | subject's left |
| back-right | 135 | over-right-shoulder zone |
| back-left | 225 | over-left-shoulder zone |

Fixed shots still record start = end. Over-shoulder names whose shoulder and whom we look at.

## Coverage is grammar, not solitude

| Type | Means | Does not mean |
|------|-------|----------------|
| Master | geography and full blocking | the only shot needed |
| Two-shot | relationship in one frame | no close-ups allowed later |
| OTS | looking past one body at the other | the near person left |
| Single | clean single composition | the other person left the room |
| Reaction | listener under pressure | speaker vanished |
| Insert | object or hands | a new location |
| Cutaway | breathing room or hidden information | occupancy reset |
| POV | named owner's eye line | a selfie |

Translate labels before they enter a model prompt:

- OTS-A -> camera at A's back-right, A's shoulder in the near foreground, focus on B
- Single-B -> clean close or medium on B; if A remains in the space, keep A offscreen or as a fragment

Emotion intensity may suggest closer framing. It must not override occupancy.

## Coverage plan is optional grammar

For a dialogue scene, a short coverage list is useful. It is not a required form, not a quota, and not a reason to delete same-space partners.

| Type | Use it to |
|------|-----------|
| Master | plant geography and who is present |
| Two-shot | show the relationship in one frame |
| OTS | look past one body at the other |
| Single | clean face or torso; partner stays in occupancy |
| Reaction | keep the listener alive |
| Insert | hands, collar, object, evidence |
| Cutaway | breathe; do not reset occupancy or pose |

Write the list only when it helps choose the next camera. Do not fill every scene with Master + OTS + Singles + Inserts because a Hollywood template exists. Never treat Single as 独自一人.


## Narrative lines

Reference images follow the approved scene and image-state relationships, not raw shot numbers. Inside one line, lock space, light, wardrobe, and occupancy. Across a flashback or dream line, break those looks on purpose. When returning to a line, inherit that line's last state, not the adjacent shot from another line.

**用户可以否决一切**, including a coverage pattern, a clock position, or a translation into prompt language.
