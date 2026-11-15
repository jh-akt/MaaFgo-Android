# MaaFgo-Android

基于 **MaaFramework-Android** 共用 Root 框架的独立 FGO 应用。应用包名为
`com.maaframework.android.fgo`，与上游 MaaFwApp 外壳不同。

- Android 11+、ARM64、需要向本应用授予 Root。当前不支持 Shizuku 或 x86_64。
- 主题、首页、任务、设置、日志、Activity 生命周期与 `MaaHostViewModel` 均由框架提供，应用只保留品牌和项目配置。
- B 服与日服资源，共 26 个任务，首次默认仅勾选登录。
- 1280×720 / DPI 240 虚拟屏，原生战斗、任务选项、预设和配置导入导出。
- 自动获取上游 Android 发行包，成套更新项目资源、Agent 和运行时，再应用本地覆盖。

## 来源和运行时

`upstream.lock.json` 固定 [xlxyvergil/MaaFgo v2.0.25](https://github.com/xlxyvergil/MaaFgo/releases/tag/v2.0.25)
及其 ARM64 APK SHA-256。构建脚本仅提取上游 APK 中经过 Android 转换的 `pi.zip`、
Python bundle 和 Maa 原生库；不使用上游 Activity、DEX、Shizuku 或外壳 JNI。

内置 MaaFramework 5.14.3、CPython 3.13.15、NumPy、OpenCV、OCR、助战与关卡 YOLO 模型。
脚本把 Python bundle 整理为框架可识别的标准目录，增加 Android Agent 入口，并保留
上游许可文件。当前还应用下述入口和等待时间适配；不会直接同步桌面版 Agent。
上游源码提交及完整来源见 lock 文件；参考源码可克隆
到同级 `MaaFgo/`。lock 固定的是可离线使用的内置基线；在线资源更新不改写 lock。更换内置版本时同时更新 manifest 的 `bundled_version` 与兼容性检查。

## 自动更新与本地覆盖

设置页“自动更新上游资源”默认开启。应用在前台每 6 小时检查一次
[xlxyvergil/MaaFgo 的最新正式发行版](https://github.com/xlxyvergil/MaaFgo/releases/latest)，
任务正在准备、运行或停止时延后；失败后 30 分钟重试，也可在首页手工检查。
关闭应用不会被定时唤醒，已经开始的下载会尽量完成，下次可从 `.part` 续传。

更新顺序：匹配 ARM64 Android APK → 校验大小和 GitHub SHA-256 → 提取配套资源与
运行时 → 校验兼容性 → 应用本地覆盖 → 校验目录与 Agent → 事务切换。
不会安装或使用上游 Android 外壳。资源更新不替换本应用 APK；框架 UI 或 JNI 更新
仍需安装新版 MaaFgo-Android。当前只接受 MaaFramework 5.14.3、Python 3.13.15、ARM64
的兼容发行包；不匹配时保留原版本并提示升级本应用。

所有项目适配集中在 `app/src/main/assets/project_overlay/overlay.json` 和同目录附件。
首次打包与每次在线更新都执行这一份规则：主线入口、30 分钟等待、日服战败识别、
默认第一位技能目标、Android Agent 入口与中文目录映射。精准文本替换或 JSON 预期值
与上游不再匹配时，更新失败并保留原资源，防止适配悄悄丢失。重复应用不会叠加修改。
需要修改行为时改这份本地覆盖，不修改生成目录或上游仓库；规则格式见
[框架说明](MaaFramework-Android/docs/RESOURCE_UPDATES.md)。

下载缓存位于应用外部文件目录的 `maaframework-resource/maa-fgo/`，保留当前和上一代
完整资源；清除资源缓存后回到 APK 内置基线。任务选项与运行目录 `config/` 保留，
资源包不能覆盖用户数据。新版 APK 修改覆盖规则后，旧规则生成的在线资源会失效，
先回到内置基线，再生成与新版覆盖一致的在线资源。

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
python3 tools/prepare_upstream.py --apk .cache/MaaFGO-android-arm64-v8a-v2.0.25.apk
```

验证脚本需要 `binutils`（`readelf`、`nm`）。生成内容和缓存不会提交 Git。
`key.properties` 可以配置自己的 Release 签名；不提交任何密钥。

## 使用与验收边界

安装 Debug APK → 授予 Root → 连接 Runtime → 准备运行时 → 选择区服 → 先运行登录。
战斗前核对队伍、次数和苹果选项。B 服默认直接启动游戏 Activity；同资源目录中的
小米、应用宝、享游服选项仍保留在上游任务中，但自动启动映射目前只配置 B 服和日服，
其他渠道需要单独适配和设备验收。

自动推主线可接在登录之后：Android 入口先从终端寻找 `NEXT` 章节，再交给上游的
地图、关卡列表、编队和原生战斗流程。终端滚动最多六次；不会无限滑动。
登录加载、主线切换、进本、战斗未知画面和演出等待上限延长到 30 分钟，以容纳游戏
按需下载。出现可识别界面后立即继续，点击及重试次数不增加，仍可主动停止。
这些适配在 `app/src/main/assets/project_overlay/` 中维护，
Python 源码替换要求与锁定版本精确匹配，上游变化时构建失败，需重新审查。
日服续关页还通过覆盖规则同时校验标题、撤退文字和按钮亮度，
防止战败继续等待 30 分钟；此识别本身不会点击或消费任何道具。

保留登录任务时，重试前应回到终端。上游登录流程不能识别所有中间页面，尤其是
上次中断后留下的助战页。选择“使用编辑器/chaldea配置”助战前必须启用并导入方案；
单关调试可选“首个助战”、默认策略、推进 1 关、不食用苹果、不使用灵脉石。
进入战斗后，在战斗菜单中关闭技能二次确认（日服为“スキル使用確認”）；
上游会关闭并跳过“技能使用”弹窗，不会代为确认释放。

原生战斗中，从者技能未指定我方目标时，默认选择当前前排第 1 位（最左侧），
而不是施放者自己。编辑器 / Chaldea 方案显式指定的目标仍优先生效；自身技能、
全体技能和专属技能流程保持原有处理。此规则由本项目的 `project_overlay/overlay.json`
在打包和在线更新时覆盖，不修改上游仓库或在共用框架中硬编码 FGO 逻辑。

0.2.0 已通过本地构建、74 项单元测试和 APK 完整性检查；使用上游 v2.0.25 与
v2.0.26 的真实 Android 发行包验证了解包、运行时兼容检查和同一覆盖规则的重复执行。
尚未在手机上验证新版本。
以下设备结果来自此前版本，按当前要求暂停手机调试。

本项目已验证构建、真实资源目录解析、任务默认选中、预设禁用项、原生依赖与 APK
完整资源。已在 Root 真机验证运行时准备、Python/NumPy/OpenCV/Agent 加载、日服登录、
终端进入主线、自动选卡与宝具、登录及战斗等待期间的主动停止。关闭技能确认后，
已验证实际释放技能与目标选择；日服第 5 回合战败后正确识别并停止，未消费复活道具。
真机续关页与撤退确认弹窗的识别回放通过。当前尚未验证通关结算；上游自身外壳的验收结果
不等于本项目已验收。APK 检查会核对全部非隐藏资源，包含下划线开头的 Python 包，
防止 Android 默认资源过滤导致运行时缺少 NumPy 等依赖。

运行数据位于框架运行目录中的 `config/`；重新准备运行时保留此目录。设置页的配置
导出仅备份宿主运行配置，不包含库存、Chaldea 队伍和羁绊数据。清除应用数据或卸载
前需另行备份这些文件。

本仓库通过子模块固定共用框架版本。发布时先推送框架，再推送本仓库，
确保远程 CI 能检出 `.gitmodules` 指向的框架提交。克隆后执行
`git submodule update --init --recursive` 初始化框架依赖。

## 许可

MaaFgo 项目资源和 Agent 遵循上游 AGPL-3.0，见 `LICENSE`。共用框架、原生依赖及
Python 第三方包保留各自许可；上游 Python/OpenCV 许可随 runtime 一同打包。
