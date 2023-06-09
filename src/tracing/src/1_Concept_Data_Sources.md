#  1. Concept - Data Sources

**OpenTelemetry**  支持下面各种不同的数据源。

## Traces
`Traces` 用于跟踪单个请求的处理进度，每个 `Trace` 会在应用的每个服务中进行处理，而请求则可能是通过用户侧或是应用自身发起的。分布式的跟踪一般由跨进程、网络及各种安全边界的调用形式来呈现。每个 `Trace` 中的工作单元称为 `Span`；一个 `Trace` 是一颗由 `Span` 组成的树。`Span` 表示一个请求触发了一个独立的服务或组件在整个系统中的流转信息，每个 `Span` 都会有一个 `Context`，其中包含能表示当前请求的全局唯一的标识符。同时 `Span` 还能够提供 `Request`、`Error`、`Duration` _(RED)_ 这些能用来帮助调试可用性跟进行性能检测使用的指标 `Metrics` 。

`Trace` 会包含一个根级别的用来表示端对端之间请求整体延时信息的  `Span` ，你可以把他当成一个逻辑性的操作，比如网页应用点击了一个按钮来将某个产品加入购物车，这个根 `Span` 就是用来确认中断用户在点击按钮到最后整个操作成功或失败到展示给用户所消耗的时间 *(即要么商品成功加入购物车要么出错)*。一个 `Trace` 会由一个根 `Span` 跟若干个子 `Span` 来组成，他们同时也表示了对应操作在整个请求过程中的位置。每个 `Span` 包含了当前操作的元数据，比如名称、起止时间、属性、事件跟状态等。

为了在 `OpenTelemetry` 中创建跟管理 `Span`，`OpenTelemetry API` 提供了 `tracer` 接口。 这个对象跟踪当前处于处理中的激活的 `Span`，并允许你通过他对当前的 `Span` 进行一些诸如添加 `Attributes` 、`Events` 信息的操作，并且当当前工作完成后结束本次的跟踪。通过 `Trace Provider` 在多个处理中可以创建一个或多个 `Trace` 对象，他提供了一个工厂接口提供了根据不同的配置创建多个 `Tracer` 的能力。

通常来说，一个 `Span` 的生命周期类似下面的描述：

-  一个服务接收到了一个请求，如果存在对应的 `Header` 信息时，会有一个 `Span Context` 会通过请求的 `Header` 信息被创建出来
- 一个新的 `Span` 会作为子节点从提取的 `Context` 创建出来，如果 `Context` 不存在，则新的 根 `Span` 会被创建出来
- 服务开始处理当前的请求时，一些额外的 `Attribute` 跟 `Event` 会被添加到对应的 `Span` 中，用来提高当前 `Span` 对应请求的可理解性，比如机器的主机名或者是一些其他的标识符
- 可能会创建一些新的 `Span` 来表示一些其中某些子组件所完成的工作
- 当服务向其他的服务发出了远程服务调用时，当前 `Span Context` 会被序列化后发送给新的服务，并注入该 `Span Context` 到请求的 `Header` 或是消息中
- 当当前服务成功或失败的完成本轮处理时，`Span` 的状态会被合适的进行标识，并设置为已完成

如果需要了解更多的信息，则可以通过 [Traces Specification][1] 来得到更多关于: `Trace`、`Span`、父子关系、`Span Context`、`Attributes`、`Events`、跟 `Links` 的信息。



## Metrics

指标 `Metrics` 是在服务运行时获取的度量工具。逻辑上，在某个时刻获取的这些被称为 `Metric` 事件的度量信息并不只包含度量信息，还包括了当时所能够捕获的其他相关的元数据。应用跟请求的指标是用来判断可用性跟性能的重要标准。自定义的指标则可以更清晰的指示出可用性会如何对用户的体验跟业务产生影响。那些被收集回来的数据可以用来作为中断的告警或是触发一些调度上的决定，比如在高负载的时候来自动扩容。

`OpenTelemetry` 当前定义了三种指标仪表盘：

- **Counter** 是一个跟随时间持续增长的值 - 你可以把他想象成汽车的里程数表，他只会持续的增长；
- **Measure** 是一个跟随时间进行聚合的值，他更像是汽车上的旅程表，可以用来某个时间区间的数据
- **Observer** 是在某个时间点捕获的一组值，更像是汽车上的燃油表

除了这三个指标仪表盘，还有 *Aggregations* 聚合这个非常重要的概念需要深入理解。聚合是一种能将大量的度量值进行合并的技术，他最终能产生基于某个时间窗口的更具体或是模糊的结果。`OpenTelemetry` 的 `API` 并不提供进行这些聚合的能力，但他提供了一些基本的默认处理。通常来说，`OpenTelemetry SDK` 提供了一些常用的聚合 *(比如 Sum、Count、Last 跟  Histograms)*。用来为可视化跟其他的后端组件提供支撑。

 `Tracing` 是为了捕获请求的生命周期并为请求的各个独立的片段提供上下文，`Metric` 则倾向于提供基于聚合的一些统计信息，比如下面一些聚合的使用用例：

- 报告某个服务所使用的每个传输协议所读取的数据量
- 报告整体的数据读取量以及每个请求的数据读取量
- 报告系统调用所消耗的时间
- 报告请求的数量用于确认整体的趋势
- 报告每个处理器的 CPU 或内存的使用量
- 报告账户的平均余额
- 报告当前正在处理的请求数

如需要更多的信息，可以查看 [Metrics Specification][1]，那里包含了关于 度量、仪表盘、指标、数据、数据点跟标签等信息。



## Logs

日志是一个加上了时间戳的包含了元数据的文本记录，他可以是结构化 *(推荐)* 或是非结构化的。尽管日志是一个独立的数据源，他们依然可以跟 `Span` 进行关联。在 `OpenTelemetry` 中，任何不属于分布式跟踪或指标的数据都是日志。比如事件 `Events` 就是一种特定类型的日志。日志通常用来确认问题的根本原因，比如谁更改了什么或是产生了什么结果。

如需更多的信息， 可以查看 [Logs Specification][2]，那里包含了关于日志、定义字段、Trace Context 字段跟 Severity 字段。



## Baggage

为了能够传递 Trace 信息， `OpenTelemetry` 提供了一个简易的称为 `Baggage` 的机制来传递键值对。`Baggage` 为同一个事务中的可观察事件提供了索引，用来访问那些由之前的服务产生 `Attributes`。这为事件之间因果关系的建立提供了支持。

虽然 `Baggage` 可以用来构建其他跨越多个碎片的原型，但这个机制主要还是用来表达那些用于体现 `OpenTelemetry` 系统的可观测性的值的。

这些值可以从 `Baggage` 中获取并作为额外的指标维度来进行消费，或者是作为日志跟 `Trace` 额外的上下文信息：

- 这些额外的上下文信息可以给网络服务提供具体的请求来自哪个服务
- 一个 SaaS 提供方可以在上下文信息为接口提供请求中包含的用户或 Token 信息
- 确认某个图像服务中的故障跟特定浏览器版本的关系

如需更多的信息，可以查看 [Baggage Specification][3]。




[1]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#metric-signal
[2]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#log-signal
[3]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#baggage-signal