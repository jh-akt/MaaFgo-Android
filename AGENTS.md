# MaaFgo Android

默认中文沟通。共用框架的修改先在同级 MaaFramework-Android 中实现、验证和提交，再更新本项目子模块。

- 独立应用包名 `com.maaframework.android.fgo`，Android 11+、ARM64、Root。
- 上游来源与 SHA-256 固定在 `upstream.lock.json`；`tools/prepare_upstream.py` 提取经过 Android 适配的资源及匹配运行时。
- 生成目录 `app/src/main/assets/project/` 和 `runtime/` 不提交、不手工修改。修改转换脚本后重新生成。
- 禁止直接同步桌面 interface/Agent 覆盖 Android 资源。任务与原生库必须随同一 APK 版本更新。
- 应用仅保留品牌与项目配置；共用状态与操作使用 framework-host 的 MaaHostViewModel。
- 不提交签名密钥、机器绝对路径、构建缓存或原始设备日志。提交使用 GitHub noreply 身份。
- 构建验收：`python3 tools/prepare_upstream.py` 后运行 `./gradlew :app:assembleDebug :app:testDebugUnitTest`。
- APK 打包检查不等于设备验收；Root 授权、登录、停止、单场战斗须在设备上另行验证。
