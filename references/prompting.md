# 提示词模板

先读取 `style-profile.md`，用它描述本次风格；只加载本次用得到的模板。工具调用遵守当前环境 imagegen 技能的要求，默认用内置工具。

## 新作答页

参考图应先被图像查看工具加载。把技能目录下两张原始参考图的绝对路径传给生成工具，明确它们仅用于笔迹与纸张风格。

```text
Use case: scientific-educational.
Asset type: one A4 portrait handwritten assignment answer sheet.
Input images: Images 1 and 2 are ONLY personal-handwriting and paper-style references, not edit targets. Use only the NEW page content below for the answers.

Style: {从style-profile.md提取本次风格；保持细黑笔、自然随手与可读性。}
Composition: {按本页内容指定单栏/松散双栏/图文分区及阅读顺序。} Full sheet, flat scan, white paper, all content within safe margins.
Text and mathematics: {本页完整正确正文，按小问次序。LaTeX仅描述公式，应画成实际手写数学符号。}
Corrections: {根据本次模式填入下节的指令。}
Accuracy: preserve every required step, symbol, sign, index, matrix entry, vector orientation, unit and conclusion. Include the entire specified content; do not mix in text from the reference pages.
```

文字类科目可把use case调整为适合的文字页面类别；图形/化学结构/电路需要在正文外明确标注其位置、连接关系、标签和数值。

### 划改指令的填入

`none`：

```text
Write only the final correct content. Use natural casual penwork throughout. Include no cancelled attempts or correction strokes.
```

`light`：先基于本页内容选择一个**可选的局部落笔笔误**，或本页选择不添加。读`style-profile.md`决定粒度和笔画；不要给每页强制配额。可填入：

```text
If using the optional local pen slip described here, cancel only the mistaken character with one short diagonal slash, or two/three short roughly parallel diagonal strokes. Place the correct character just above or beside it. Keep the surrounding expression and all final mathematics correct. A page may have no correction. Do not draw X-shaped cancellation marks.
Optional local pen slip: {仅列出误写字符、正确字符及局部位置；例如某个矩阵名B应写A。若无合适位置，填“none on this page”。}
```

符号本身含有交叉笔画时，不要把原符号误认作取消标记。需要写`+`、`×`或`≠`的正确位置仍应照常保留。

## 修改已有手写页

先查看本地目标图像，再使用它作为编辑目标。新增参考图时逐个标明角色，不能把风格参考当成要改的页面。

```text
Use case: precise-object-edit.
Image 1 is the edit target. Make only the specified local changes.
Changes: {逐项写出准确位置和最终正确内容；明确矩阵行列或上标位置。}
Preserve the complete page, all other text, exercise order, proof steps, correct mathematics, handwriting, paper, layout and page number.
Return the complete page with the changes blended into the existing black-pen handwriting.
```

### 清理划改

```text
Remove both the cancellation strokes AND the cancelled incorrect writing at the listed locations. Leave only the final correct expression, with natural spacing and no leftover duplicate equals signs. Preserve mathematical minus signs, fractions, overbars, transpose/inverse exponents, brackets and all not-equal symbols.
Final expressions: {列出每处清理后应读成的内容。}
```

### 数学修正的明确表达

- 说“horizontal ROW vector `[0 1]`, with both entries on one baseline”或“two-row COLUMN vector `[0;1]`”，避免仅写模糊的vector。
- 题目用`z=Tx`时，明确`\bar A=TAT^{-1}`；用`x=Tz`时，明确`\bar A=T^{-1}AT`。沿用本题约定。
- 同一公式里被改的是一个符号时，写清应保留的邻近数字、变量与括号。
- 修订后的页面需要重新查看；修改请求里的“其他部分保持”不能代替成品核对。
