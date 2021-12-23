# 5. Concept - Distributions

`OpenTelemetry` 项目由多种不同的支持多种 [数据源][1] 的  [组件][2] 组成。对应的实现手册可以参照

- [Language-Specific Instrumentation Libraries][3]
- [A Collector Binary][4]

可以从任何实现的参考来创建新的发行版本。

## What is a distribution

不要将发行版跟 Fork 混淆，发行版是一个 `OpenTelemetry` 组件的自定义版本。一个发行版是基于现有的 `OpenTelemetry` 仓库来进行自定义的，自定义的发行版可能会包括：

- 一些为提高指定的后端或者厂商易用性的脚本
- 为指定的后端、厂商或终端用户重新适配的默认设置
- 为指定的厂商或用户添加的为配置项
- 提供比 `OpenTelemetry` 所支持的更好的测试、性能跟安全性
- 一些比 `OpenTelemetry` 所没有提供的额外功能
- 或是将 `OpenTelemetry` 的功能进行了精简

发行版大致上可以归入以下几类

- "**Pure**": 这种发行版提供跟上游版本 100% 兼容的功能，个性化的地方一般会在于提高易用性或将功能进行封装。这些个性化的可能会是为某些指定的后端、厂商或用户而做的
- “**Plus**”: 这种发行版提供了跟上游版本相同的功能的同时会对其进行加强。这些比 **Pure** 更强的个性化功能可能会包含在额外的组件中。比如会提供上游项目中未提供的支持某些特定厂商的自动仪表库或 `Exporter` 等
- “**Minus**”: 这种发行版将上游提供的功能进行了精简。比如会将自动仪表库移除，或是将 `Collector` 中的 `Receiver`/`Processor`/`Exporter`/`Extension` 等移除。这些发行版可能还会针对支持的广泛性跟安全性考虑进行了特定的加强。

## Who would create a distribution

任何人都可以创建新的发行版，现在已经有许多的[厂商][5]提供了自己的发行版。还有些终端用户如果需要用到不在 `OpenTelemetry` 项目中的组件，他们也会考虑创建自己的发行版。

## Creating you own distribution

### Collector

这篇文章 [Building your own OpenTelemetry Collector Distribution][6] 可以指导你如何去创建自己的发行版。

如果你想要创建自己的发行版本，那 [OpenTelemetry Collector Builder][7] 会是一个很好的起点。

## What you should know about distributions

`OpenTelemetry` 项目当前并未对发行版进行验证。可能在未来 `OpenTelemetry` 会像 Kubernetes 那样对发行版或者合作伙伴进行认真，来确保发行版不会被特定的厂商所限制。

[1]:	https://opentelemetry.io/docs/concepts/data-sources
[2]:	https://opentelemetry.io/docs/concepts/components
[3]:	https://opentelemetry.io/docs/concepts/instrumenting
[4]:	https://opentelemetry.io/docs/concepts/data-collection
[5]:	https://opentelemetry.io/vendors
[6]:	https://medium.com/p/42337e994b63
[7]:	https://github.com/open-telemetry/opentelemetry-collector-builder