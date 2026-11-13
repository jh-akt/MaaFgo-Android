# MaaFgo-Android

基于 **MaaFramework-Android** 共用 Root 框架的独立 FGO 应用。应用包名为
`com.maaframework.android.fgo`，与上游 MaaFwApp 外壳不同。

- Android 11+、ARM64、需要向本应用授予 Root。当前不支持 Shizuku 或 x86_64。
- 共用首页、任务、设置、日志 UI，以及 `MaaHostViewModel`，应用不复制控制逻辑。
- B 服与日服资源，共 26 个任务，首次默认仅勾选登录。
- 1280×720 / DPI 240 虚拟屏，原生战斗、任务选项、预设和配置导入导出。
- 项目资源与 Agent 随 APK 更新，不在线同步桌面版资源。

## 来源和运行时

`upstream.lock.json` 固定 [xlxyvergil/MaaFgo v2.0.25](https://github.com/xlxyvergil/MaaFgo/releases/tag/v2.0.25)
及其 ARM64 APK SHA-256。构建脚本仅提取上游 APK 中经过 Android 转换的 `pi.zip`、
Python bundle 和 Maa 原生库；不使用上游 Activity、DEX、Shizuku 或外壳 JNI。

内置 MaaFramework 5.14.3、CPython 3.13.15、NumPy、OpenCV、OCR、助战与关卡 YOLO 模型。
脚本把 Python bundle 整理为框架可识别的标准目录，增加 Android Agent 入口，保留
上游原始业务代码和许可文件。上游源码提交及完整来源见 lock 文件；参考源码可克隆
到同级 `MaaFgo/`。更新时需同时更新锁定版本并重新进行目录、原生库和设备验收。

## Linux 构建

需要 JDK 21、Python 3.13+、curl、Git、Android SDK 36、Build Tools 35.0.0、
NDK 27.0.12077973、CMake 3.22.1。设置 `JAVA_HOME` 和 `ANDROID_HOME`。

```bash
git submodule update --init --recursive
./gradlew :app:assembleDebug :app:testDebugUnitTest
python3 tools/verify_payload.py --apk app/build/outputs/apk/debug/app-debug.apk
```

Gradle 自动下载并验证锁定的上游 APK，再生成 `runtime/` 和
`app/src/main/assets/project/`。下载中断保留 `.part`，后续可续传。
已有上游 APK 时可先执行：

```bash
python3 tools/prepare_upstream.py --apk /path/to/MaaFGO-android-arm64-v8a-v2.0.25.apk
```

验证脚本需要 `binutils`（`readelf`、`nm`）。生成内容和缓存不会提交 Git。
`key.properties` 可以配置自己的 Release 签名；不提交任何密钥。

## 使用与验收边界

安装 Debug APK → 授予 Root → 连接 Runtime → 准备运行时 → 选择区服 → 先运行登录。
战斗前核对队伍、次数和苹果选项。B 服默认直接启动游戏 Activity；同资源目录中的
小米、应用宝、享游服选项仍保留在上游任务中，但自动启动映射目前只配置 B 服和日服，
其他渠道需要单独适配和设备验收。

本项目已验证构建、真实资源目录解析、任务默认选中、预设禁用项、原生依赖与 APK
内容。没有连接设备时，不能据此宣称 Root、预览触控、登录、停止、战斗已经实测通过。
上游使用其自身外壳取得的设备验收结果不等于本项目已验收。

运行数据位于框架运行目录中的 `config/`；重新准备运行时保留此目录。设置页的配置
导出仅备份宿主运行配置，不包含库存、Chaldea 队伍和羁绊数据。清除应用数据或卸载
前需另行备份这些文件。

本地创建阶段依赖尚未推送的框架子模块提交；需要先将框架提交发布到其远程仓库，
再发布本仓库，远程 CI 才能按 gitlink 完整检出。当前未进行任何远程推送。

## 许可

MaaFgo 项目资源和 Agent 遵循上游 AGPL-3.0，见 `LICENSE`。共用框架、原生依赖及
Python 第三方包保留各自许可；上游 Python/OpenCV 许可随 runtime 一同打包。
