# 第 4 步：飞书交付

只在用户要「飞书文档」时读本节。**若用户只要本地 md，跳过本节，直接交付文件。**

先加载 `lark-unified` 技能，按它的说明操作。本节只记录**已验证的坑与决策**，不重复技能里的通用用法。

## 铁律：优先用 user 身份创建

> **`--as user` 优先于 `--as bot`。**

原因：用 bot（应用）身份创建的文档，归属在应用名下，用户打不开——因为把用户加成协作者需要应用具备 `docs:permission.member:create` 等一系列权限，而实际部署通常**没开**。

症状（踩过）：
- 创建成功，但返回体里 `permission_grant.status = "failed"`、`lark_code 99991672`。
- 想自查「用户到底能不能打开」，调 `drive +permission-get-setting --as bot`，**同样被拒**（缺 `drive:drive:readonly`、`docs:permission.setting:read`）。
- 结论：**bot 身份下，你既拿不到权限、也验不了权限。** 所以别在 bot 身份上挣扎。

缺的权限清单（一次要全，否则反复授权）：
`docs:permission.member:create`、`drive:drive`、`drive:file`、`docs:doc`、`sheets:spreadsheet`、`wiki:wiki`、`bitable:bitable`、`bitable:app`。

## 前置检查（不要信任第三方状态脚本）

- **不要用 `lark_status.py` 判断是否安装**。它曾报 `state:"not_installed"` / exit 3，而 `lark-cli` v1.0.94 实际已安装且已配置——按它的结论走会白跑一圈。
- 直接用：
  - `lark-cli config show`
  - `lark-cli auth status --json`

判断要点：
- `user.status: missing` 或 `tokenStatus: expired` → user 身份不可用，需要重新授权。
- 只看 bot 状态为 `ok` 不能说明任何事，因为 bot 身份本身就打不开。

## 授权：device-code 流程

若 user 身份不可用：

1. 发起授权（用一个够用的 scope 集合，一次要全）：
   ```
   lark-cli auth login --scope "docx:document:create docs:permission.member:create docx:document:write_only" --no-wait --json
   ```
2. 取二维码给用户扫：
   ```
   lark-cli auth qrcode
   ```
   把生成的图片（如 `lark-qr.png`）用 `present_files` 展示给用户。
3. **明确告诉用户：需要用飞书 App 扫码完成授权，完成后回复一声。** 用户没完成之前，不要假设授权已好。
4. 完成后 `auth status --json` 应显示 user 为可用。

**失败模式**：用户中途离开、没扫码。此时不要反复重试或静默降级成 bot，直接把「链接可能打不开」如实说明，并把本地文件交付给用户——**本地 md 是保底交付物，永远先给。**

## 创建与回读

- 创建：`docs +create`（导入第 3 步产出的 md）。
- 回读校验：**flag 是 `--doc`，不是 `--doc-token`**（踩过，报错信息里才给出正确 flag）。
  ```
  lark-cli docs +fetch --doc <token>
  ```

## 交付话术（必须包含的三句）

1. 文档链接。
2. 打开文档的方法（**演示模式**入口在文档右上角，方向键翻页）——主讲不一定知道。
3. 若权限状态不确定，如实说明，并附上本地 md 路径作为兜底。

## 完成判据

**用户能打开链接看到内容**；或（权限处置不了时）**已明确告知权限情况并交付了本地文件**。二者必居其一，不能既没验证也没说明。

## 反面清单

- ❌ 用 `--as bot` 建完就说「已交付」——用户很可能打不开，且你验证不了。
- ❌ 引用 `lark_status.py` 的 `not_installed` 结论。
- ❌ 用 `--doc-token` 调 fetch。
- ❌ 只给链接不给「怎么切演示模式」。
- ❌ 权限失败还装作成功，不告诉用户兜底文件在哪。
