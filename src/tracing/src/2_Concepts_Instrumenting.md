#  2. Concepts - Instrumenting

`OpenTelemetry` 项目可以用于快速构建应用的仪表信息的工具。仪表库为每个语言都提供了一个核心的库。他们不一定会提供额外的用于自动构建的仪表库或是其他的非核心组件。比如 Java 的仪表库提供了下面的几个库：

- [Core](https://github.com/open-telemetry/opentelemetry-java) 提供了一个实现了 OpenTelemtry API 跟 SDK 的用于手动构建的工具库
- [Instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation) 提供所有核心功能和各种库跟框架的自动检测的工具库
- [Contrib](https://github.com/open-telemetry/opentelemetry-java-contrib) 可选的类似 JMX Metric Gather 的组件

一些仪表库，如 `Ruby` 的则提供了单个仓库来同时提供手动跟自动的工具库。一些其他的语言，如 JS 则从 `Contrib` 库中分离出 `Core` 库，并以此将其分离成独立的两个分别实现手动跟自动能力的仪表库。

`OpenTelemetry` 具体的安装机制要取决于具体的开发语言，但他们大部分都有下面几节所具有的共同点。



## Automatic Instrumentation

### Add dependencies

我们需要添加一个或多个依赖来启用自动仪表库，具体要添加的依赖则取决于具体的语言。但这些依赖都需要实现 `OpenTelemetry API` 跟 `SDK` 的功能。有一些语言需要为每个仪表库的单独添加依赖。可能还会需要添加对 `Expoter`  的依赖。要了解更多关于 `OpenTelemetry API` 跟 `SDK` 的信息，则需要参考 [Specification Repository](https://github.com/open-telemetry/opentelemetry-specification)。

### Configure OpenTelemetry Instrumentation

配置信息可以通过环境变量或是特定语言的机制来提供，比如在 Java 中则是使用系统属性 *(System Properties)*。但我们至少需要提供服务的名称来标识需要自动构建的服务。如下面所列的，还有一些其他的信息是可以配置的：

- 指定数据源的配置信息
- `Exporter` 的配置信息
- `Propagator` 传播器的配置信息
- `Resource` 资源的配置



## Manual Instrumentation

### Import the OpenTelemetry API and SDK

首先我们需要将 `OpenTelemetry` 引入我们的服务，如果你在开发通用库或其他一些会被一些可执行的程序使用的组件，那你应该只引入对 `API` 的依赖。如果你的目标是一个可以独立运行的程序或服务，那应该同时引入 `API` 跟 `SDK`。如果想了解更多关于 `OpenTelemetry` 的 `API` 跟 `SDK` 的相关信息，可以查看 [Specification Repository](https://github.com/open-telemetry/opentelemetry-specification)。

### Configure the OpenTelemetry API

为了能够创建 `Trace` 跟 `Metric` 信息，首先应该创建 `Tracer` 以及在需要的情况床架 `Meter Provider`。通常我们会建议 `SDK` 为这些对象的获取提供一个默认的单例 `Provider`，这样你就可以直接通过 `Provider` 得到所需的 `Tracer` 或是 `Meter` ，并为他们提供对应的名称或版本。你在这一步所选择的名称会作为后续仪表信息的标识符，所以如果你是在开发一个库，那你应该将这个名称的设置置于库的初始化之后 *(比如 com.legittimatebusiness.myLibrary 或其他的唯一标识)*，因为这个名称会将所有的 `Span` 跟 `Metric Event` 建立统一的命名空间。同时我们也推荐为其提供一个指定的版本 *(如semver:1.0.0)* 用来明确当前所使用的服务的对应版本。

### Configure the OpenTelemetry SDK

如果你在构建的是一个服务程序，还会需要为 `SDK` 提供对应的配置信息，来指示应该如何导出 `OpenTelemetry` 的数据到后端。我们推荐将这些配置信息在程序中通过配置文件或其他的机制来提供。同样的每种编程语言可能都有相应的合适的配置。

### Create Telemetry Data

在配置好 `API` 跟 `SDK` 后，就可以开始用从 `Provider` 中得到的 `Tracer` 跟 `Meter` 对象来创建 `Trace` 跟 `Metric Event` 信息了。你还可以使用一些便捷的插件或整合工具来创建 `Trace` 跟 `Metric Event` ，可以从这个 [Registry](https://opentelemetry.io/registry) 或对应语言的仓库获取更多的信息。

### Export Data

在你创建了 `Telemetry` 数据后，你需要将它发送到某个指定的地方，`OpenTelemetry` 主要支持两种方式来从你的程序中导出这些数据到对应的后端，你可以从程序直接发送也可以通过 [OpenTelemetry Collector](https://opentelemetry.io/docs/collector) 进行代理。

在程序内部的导出需要你首先去导入所依赖的一个或多个 `Expoter`，以及相关的库，他们需要用来转换内存中的 `OpenTelemetry` 的 `Span` 及 `Metric` 数据为指定格式给诸如 `Jaeger` 或 `Prometheus` 的分析工具。并且，`OpenTelemetry` 通过 `SDK` 支持另一个广为人知的 `OTLP` 协议，这个协议可以用来发送数据给 `OpenTelemetry Collector` ，他是一个独立的可执行程序，可以用来作为代理或是服务的 `SideCar`，或是一个独立的主机。`Collector` 可以配置转发跟导出对应的数据到指定的分析工具。

除了 `Jaeger` 跟 `Prometheus` 这些开源工具外，还有越来越多其他的公司支持从 `OpenTelemetry` 中获取数据了，具体的信息可以参考 [这个](https://opentelemetry.io/vendors) 页面。