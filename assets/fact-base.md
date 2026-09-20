# 事实底库（fact-base）

> **版本：v1.0.0（2026-09-20）** —— 所有分享产出的唯一事实来源。数字过期先更新本文件再产出。
> 技术分享定位：每条陷阱给足"现象→根因→解法→代码"，支撑长文写作。

## 一、产品事实

| 项 | 事实 |
|----|------|
| 仓库 | **https://github.com/DczAnt/rk3xx-chip-dev**（public，Apache 2.0，v2.0.1） |
| 定位 | Rockchip RK3XX 芯片开发 AI 技能包：挂到 AI 编程智能体上的踩坑经验库 |
| 支持芯片 | RK3562 / RK3566 / RK3568 / RK3576 / RK3588 / RV1106（6 款） |
| 知识规模 | 56 个陷阱 + 46 条准则，8+ 项目模板（C/C++/Go/Rust/CMake，含零拷贝管线模板） |
| 架构特点 | 参数化无硬编码（boards/registry.yaml 配置 IP/凭据，脚本走 args/env）；多智能体适配（CodeArts/Cursor/Claude Code/Aider/Continue/Cline）；references/（RK 专有）+ knowledge/（通用工程）双库分离 |
| README | 含《如何自制 AI 技能包》五步法教程（积累踩坑记录→陷阱三元组→SKILL.md→参数化脱敏→挂载沉淀） |
| 核心理念 | **坑踩一次，写进技能包，AI 之后所有项目不再踩**——经验的复利 |

## 二、实测性能数字（实践项目：RK3576 八路 AI 视频监控）

> 项目仓库：https://github.com/DczAnt/ai_video_monitor_rk3576

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 总推理 fps | 19.96（4 路） | **84.27（8 路）** | 4.2× |
| 每路检测 fps | 5.0 | **10.53** | 2.1× |
| NPU Core0 / Core1 | 26% / 0% | **61% / 60%** | 第二核从躺平到拉满 |
| CPU 占用 | 33.8% | **18.7%** | 近半下降 |
| JPEG 编码 | CPU 软编 | **VPU 硬编**（mjpeg_rkmpp） | 消除 sws_scale+CPU 编码 |
| 内存 | — | 244MB / 8GB（3.1%） | 8 路并发余量 |

**五阶段优化历程**：基线 19.96 → 改跳帧 33.71 → 双核 NPU+绑核 62.42 → RGA 双实例+8 路 63.66 → VPU 硬编 **84.27**。

**架构一句话**：N 路 RTSP → ffmpeg 硬解(hevc_rkmpp) → RGA 缩放 → RKNN 推理(YOLOv8n 640×640) → 区域判定 → 环形缓冲 IPC → Go 服务器（WebSocket+SQLite+Webhook/MQTT）+ DRM HDMI 网格。全链路 DMA-BUF 零拷贝，CPU 不搬像素；三级守护（进程 15s→服务 5s→硬件看门狗 30s）。

## 三、陷阱库（技术分享弹药，每条独立可用）

### T1 交叉编译 GLIBC 崩溃（受众最广）

- **现象**：容器（glibc 2.35）编译通过，板子（glibc 2.31）运行报 `version GLIBC_2.34 not found`。
- **根因**：动态链接器要求符号版本 ≤ 板子 glibc；容器默认 crt/链接参数按容器 glibc 生成。
- **解法**（板子 crt 三要素）：`-nostartfiles` + 板子 glibc 的 Scrt1.o/crti.o/crtn.o + `--sysroot=<板子glibc sysroot>`。
- **决策树**：不依赖 SDK .so → 静态链接（-static / musl，零 glibc 依赖）；仅 librga.a → 可静态；含 librknnrt/librockchip_mpp（只有 .so）→ 必须动态 + 板 crt 三要素。
- **适用**：RK3568（glibc 2.31）典型；RK3576 glibc 2.35 可板上原生编译绕开。

### T2 NPU 双核"假激活"（最有故事性）

- **现象**：RK3576 双核 NPU，Core1 利用率永远 0%，总推理只有单核能力。
- **根因**：单 RKNN context 上 `rknn_set_core_mask(ctx, RKNN_NPU_CORE_0_1)` 驱动不认（枚举 CORE_0=1/CORE_1=2/CORE_0_1=3）。
- **解法**：2 个独立 context + 2 个推理线程，分别绑核，各处理一半通道：

```c
rknn_context ctx0, ctx1;
rknn_init(&ctx0, model, len, 0, NULL);
rknn_set_core_mask(ctx0, RKNN_NPU_CORE_0);
rknn_init(&ctx1, model, len, 0, NULL);
rknn_set_core_mask(ctx1, RKNN_NPU_CORE_1);
// 每个 context 独立 input_mem/output_mems，线程间无锁竞争
```

- **效果**：Core1 0% → 60%，总推理 19.96 → 84.27 fps 中的最大单项贡献（62.42 阶段）。
- **关联坑**：RK3568 NPU 单核，core_mask 只认 AUTO/CORE_0，开"双核"静默失败。

### T3 mjpeg_rkmpp 拒绝 DRM_PRIME 输入

- **现象**：VPU 硬编 JPEG 时报 `Unsupported input pixel format`。
- **根因**：该 build 的 mjpeg_rkmpp 不接受 `AV_PIX_FMT_DRM_PRIME`。
- **解法**：输入用 `AV_PIX_FMT_NV12` + 软件帧（mmap DMA-BUF 后 memcpy 345KB/帧），编码仍是 VPU 硬件执行，消除 sws_scale 色彩转换 + CPU 编码。

### T4 RGA 四连坑（一次说清）

1. `imsetColorSpace` 一调，`improcess` 必失败——不要调用。
2. 成功码是 `IM_STATUS_SUCCESS = 1`，不是 0（`rs == 0` 判错）。
3. 输入输出 stride 须 16 字节对齐。
4. 跨设备 buffer（NV12 from MPP）必须用 6 参数版 wrapbuffer 传真实 stride，4 参数版自动算 stride 会出错。
- **RK3576 附加**：双 RGA 均衡用 `im_opt_t.core = IM_SCHEDULER_RGA2_CORE0/CORE1`，且必须用 C++ 10 参数版 improcess（C 版无 im_opt_t 参数）。

### T5 MPP 硬解三坑

1. 输入是**裸码流**（无封装），须先 ffmpeg 解封装再 `decode_put_packet`。
2. `decode_put_packet` 返回 `MPP_ERR_BUFFER_FULL(-1012)` → do-while：先 `decode_get_frame` 取帧再重试 put。
3. 分帧用新 API：`mpp_dec_cfg_set_u32(cfg, "base:split_parse", 1)` + `MPP_DEC_SET_CFG`，旧的 `MPP_DEC_SET_PARSER_SPLIT_MODE` 已废弃；split_parse=1 后 Info Change 只需 `MPP_DEC_SET_INFO_CHANGE_READY`。
4. H.264/H.265 需 20+ buffer 组（参考帧多），其他格式 10+。

### T6 ffmpeg-rockchip 零拷贝管线（硬核卖点）

```c
// hevc_rkmpp 硬解 → AVFrame(DRM PRIME) → 提取 DMA-BUF fd
AVDRMFrameDescriptor *desc = (AVDRMFrameDescriptor *)frame->data[0];
int fd = desc->objects[0].fd;
// → RGA importbuffer_fd(fd) 硬件缩放 → RKNN rknn_set_io_mem(fd) 推理
// 全程 DMA-BUF 零拷贝，CPU 不参与像素搬运
```

- **关键限制**：命令行 `hwdownload`/`scale_rkrga` 在板上有格式协商问题，零拷贝管线只能用 C API。
- **C++ 注意**：ffmpeg 头文件无 extern "C"，必须手动包裹；静态库直接给 .a 路径，不用 -l/-L。

### T7 CamStats 结构体对齐（C/Go 共享内存）

- **现象**：C++ 侧 CamStats 加一个字段，Go 侧 CH1 之后所有通道数据乱码。
- **根因**：共享内存偏移双侧硬编码：C++ `sizeof(CamStats)=40`（6×uint32 + char[16]），Go `off := 40 + ch*40`。
- **解法**：单侧改动必须双侧同步；改完删 `/dev/shm/ai_video_ring` 并重启（旧数据按错误偏移读）。

### T8 Zone 告警三处不一致（AI 最易写出的"看起来对"代码）

- **现象**：误报 + 漏报并存。
- **根因**：C++ 用 zone 内 count、Go/前端用全画面 PersonCount；C++ 用 `>`、Go 用 `>=`；threshold=0 语义三处不同。
- **解法**：**单一数据源**——C++ ZoneManager 算好 `alert` 布尔字段输出 JSON，Go/前端只消费不重算。

### T9 部署调试连环坑（运维向）

1. `systemd Restart=always` 下 kill -9 后 6 秒自动复活，新二进制永远覆盖不上 → dev_deploy.sh 双模式（stop 禁自启 / start 恢复）。
2. scp 覆盖运行中二进制报 `dest open: Failure` → 必须先 stop。
3. Windows 编辑的 .sh 上板须 `sed -i 's/\r$//'` 修 CRLF。
4. Docker 编译后验证新代码：`strings binary | grep <新字符串>`（Go build cache 陷阱）。

### T10 RKNN 输入格式（新手必踩）

- 输入 `RKNN_TENSOR_NHWC`（非 NCHW），类型 UINT8，RKNN 内部自动归一化；RK3568 量化为 INT8。
- OpenCV 读取是 BGR，推理前必须 `cvtColor(BGR2RGB)`——推理结果颜色/置信度异常先查这里。

## 四、实践项目工程亮点（长文素材）

- 全链路零拷贝：ffmpeg→DRM PRIME fd→RGA→RKNN，CPU 全程不搬像素
- CPU big.LITTLE 绑核：解码线程→A53(CPU0-3)，推理线程→A72(CPU4-7)，pthread_setaffinity_np
- 环形缓冲 IPC：mmap 共享内存 128 slots×256KB，C++→Go；快慢路径分离（快路径 <10ms/tick，慢路径异步 goroutine + 非阻塞 drop）
- Web 动态配置：通道数/RTSP/AI 开关/模型在线改，一键应用重启
- 三级守护：ai_monitor 崩溃 15s 恢复 / ai_server 崩溃 5s 重启 / 系统挂死看门狗 30s 重启
- 告警链路：Webhook/MQTT/蓝牙 A2DP 音频、跨通道预警、方向穿越检测（ByteTrack）

## 五、选题池（按读者收益排序，用一条划一条）

| # | 选题 | 平台 | 核心知识点 | 素材 |
|---|------|------|-----------|------|
| 1 | 我把 56 个 RK 芯片开发的坑，做成了 AI 编程助手的"记忆" | 公众号/知乎 | skill 方法论五步法（对应 README 教程） | §一 + T1-T10 摘要 + 五步法 |
| 2 | NPU 双核利用率 0% 排查实录 | 全平台 | T2 完整版（现象→排查→根因→代码） | T2 + 数字表 |
| 3 | RK 芯片交叉编译：一条决策树终结 GLIBC 兼容问题 | CSDN/知乎 | T1 决策树 + 完整编译命令 | T1 |
| 4 | RK3576 8 路视频监控 4.2 倍优化全记录 | 公众号 | 五阶段优化 + 每阶段数字 | §二 |
| 5 | 全链路零拷贝：DMA-BUF 在 RK 平台的实践 | 知乎/掘金 | T6 代码级讲解 | T6 + T3/T4 |
| 6 | 如何给你的 AI 编程助手做"技能包" | 公众号 | 五步法实操 | §一 README 教程 |
| 7 | 嵌入式 AI 项目上线前，我必查的 9 个部署坑 | CSDN | T9 + T7 + T8 | T7-T9 |
| 8 | MPP 硬解避坑：从 BUFFER_FULL 到 Info Change | CSDN | T5 完整版 | T5 |
| 9 | RGA 用对了省一半 CPU：四个必踩坑 | CSDN | T4 | T4 |
| 10 | AI 写嵌入式代码为什么总翻车？我靠这个方法根治 | 公众号/知乎 | skill 价值叙事 + T2/T8 案例 | §一 + T2/T8 |