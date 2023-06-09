# 4. Concept - Data Collection

`OpenTelemetry` 项目通过 `OpenTelemetry Collector` 提供了便捷的收集遥测数据的能力。`OpenTelemetry Collector` 提供了一个与具体厂商无关的实现，描述应该如何接收、处理跟导出遥测数据。为了能够支持将开源的可观测数据格式 *(如 Jaeger 跟 Prometheus 等)* 发送到一个或多个开源的或商业的后端，他移除了运行、操作跟管理多个 Agent 或 Collector 的功能。另外，`Collector`允许终端用户能够控制他们的数据。默认的情况下 `Collector` 是接收仪表库的遥测数据的默认选择。

> `Collector` 还能提供分布式的支持，具体的可以查看 [这里](https://opentelemetry.io/docs/concepts/distributions) 来获取更多的信息

## Deployment

`OpenTelemetry Collector` 提供了一个独立的二进制程序以及两种部署的方式：

- **Agent**: `Collector` 的实例跟应用一起运行，或者是在同一个机器上作为一个程序来运行 *(比如二进制文件、SideCar 或 Daemonset)*
- **Gateway**: 一个或多个 `Collector` 实例作为独立的服务 *(比如作为一个 Container 或 Deployment)* ，比如每个集群、数据中心、区域都有一个

更多的如何使用 `Collector` 的信息可以参考 [Getting Started Documention](https://opentelemetry.io/docs/collector/getting-started)。

## Components

`Collector` 由下面的几个组件组成

- **Receiver** 定义了如何将消息接收到 `Collector`，他们可以是基于 Push 或是 Pull 模式的
- **Processor** 定义了需要对接收的数据进行何种处理
- **Exporter** 定义了要将接收到的数据发送到什么地方，他们也可以是基于 Push 或是 Pull 模式的

这些组件是通过 `PipeLines` 启用的，这些组件可以通过 YAML 同时定义多个实例。

关于这些组件的更多信息可以参考 [Configuration Documentation](https://opentelemetry.io/docs/collector/configuration)。

## Repositories

`OpenTelemetry` 项目提供了两种版本的 `Collector`:

- **[Core](https://github.com/open-telemetry/opentelemetry-collector/releases)** 基础组件，如配置跟通用的可适配的 `Receiver`、*Processor*、`Exporter` 跟其他的扩展。为流行的开源项目如 Jaeger、Prometheus 跟 Fluent 等项目提供了支持。
- **[Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/releases)** 所有的组件都在 Core 版本上面做了增强或者是提供了其他实验性的组件。包括了更为特化了的适配特定厂商的 `Receiver`、`Processor`、`Exporter` 跟扩展。

