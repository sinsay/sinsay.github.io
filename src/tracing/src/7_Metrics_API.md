# 7. Metrics - API

[TOC]



Metrics API 包含下面几个主要的组件

- `MeterProvider` 作为提供 `Meter`  的入口
- `Meter` 则负责创建 `Instruments` 
- `Instruments` 则负责报告本章所涉及的各种 `Measurements` 指标

简单来介绍，他们之间的层级结构是这样的 

```python
+-- MeterProvider(default)
    |
    +-- Meter(name='io.opentelemetry.runtime', version='1.0.0')
    |   |
    |   +-- Instrument<Asynchronous Gauge, int>(name='cpython.gc', attributes=['generation'], unit='kB')
    |   |
    |   +-- instruments...
    |
    +-- Meter(name='io.opentelemetry.contrib.mongodb.client', version='2.3.0')
        |
        +-- Instrument<Counter, int>(name='client.exception', attributes=['type'], unit='1')
        |
        +-- Instrument<Histogram, double>(name='client.duration', attributes=['net.peer.host', 'net.peer.port'], unit='ms')
        |
        +-- instruments...

+-- MeterProvider(custom)
    |
    +-- Meter(name='bank.payment', version='23.3.5')
        |
        +-- instruments...
```

> MeterProvider 用来创建 Meter, 每个 Meter 都会使用唯一的名称来创建，并负责一个独立的模块，在这个 Meter 下面会根据具体的指标来创建对应类型的 Instrument，比如上图中的 `io.opentelemetry.contrib.mongodb.client` 负责跟踪 MongoDb 的客户端信息，客户端信息中又包含了客户端的异常统计指标 _(`Counter`)_， 客户端的查询耗时指标 _(`Histogram`)_

## MeterProvider
`Meter` 可以通过 `MeterProvider` 来创建跟访问，在使用它创建 `Meter` 的时候应该提供一个唯一有意义的名称，比如 `io.opentelemetry.contrib.mongodb` 来描述具体需要监控的对象、模块。

## Meter
`Meter` 的责任是创建 `Instruments`，即各种所需的指标，需要注意的是 `Meter` 不应该去负责各种配置问题，配置的责任应该是在 `MeterProvider` 中。
### Meter Operations
`Meter` 可以使用下列接口来创建 `Instruments`:
- [Create a new Counter](#Counter)
- [Create a new Asynchronous Counter](#Asynchronous Counter)
- [Create a new Histogram](#Histogram)
- [Create a new Asynchronous Gauge](#Gauge)
- [Create a new UpDownCounter](#UpDownCounter)
- [Create a new Asynchronous UpDownCounter](#Asynchronous UpDownCounter)

## Instrument

`Instruments` 会用来报考指标信息，每个 `Instrument` 都会具有下列的信息

- Name 名称
  - 非空的、大小写敏感的、最大长度为 63 个字符的ASCII 码符号
- Kind 类型
  - 可以是下面将列举的各种 `Instrument`，并且会分成同步跟异步两种，具体可以看下面的解释
- 可选的 Unit 单元
  - 当 Unit 为空或未提供时，API 的 SDK 需要将其作为空字符串来对待
  - 大小写敏感，即 `Kb` 跟 `kB` 会被视为是不同的单元
- 可选的 Description 描述

### Synchrounous and Asynchrounous

`Synchronous` 同步的意味着需要应用或者业务自己去处理相关的逻辑，比如 HTTP 客户端会使用 `Counter` 来记录接收到的字节数，并且同步的 `Instrument` 可以跟当时执行的上下文建立关联

`Asynchrounous` 异步的意味着处理的逻辑是一个由用户注册到 `Instrument` 的回调函数，并且他只会在触发收集指标的时候被调用，比如一个嵌入式的软件会使用异步的 `Gauge` 每隔 15 秒收集一次传感器的温度，这意味着这个函数会每隔 15 秒被调用一次，最后异步的指标信息无法跟当时执行的上下文进行关联。



### Counter

`Counter` 是一个只支持非负增长信息的同步的 `Instrument`。比如我们会用 `Counter` 来记录：

- 统计接收的字节数
- 统计已完成的请求数
- 统计已创建的账户
- 统计检查点执行的次数
- 统计 HTTP 500 错误的个数

#### Counter Creation

`Counter` 只能通过 `Meter` 来进行创建，用于创建 `Counter` 的接口需要接收三个参数

- Name 名称，同样遵循 Instrument 的命名规范
- 可选的 Unit，同样遵循 Instrument 的单元规范
- 可选的 Description，同样遵循 Instrument 的描述规范

下面是创建接口的示例

```python
exception_counter = meter.create_counter(name="exceptions", description="number of exceptions caught", value_type=int)
```

#### Counter Operations

##### Add

为 Counter 递增一个指定的非负值，该接口还可以接收一个额外的 `Attributes` 属性参数，这个属性参数应该可以在调用 Add 的时候动态的赋值，而不是在创建 `Instrument` 的时候进行注册，下面是接口的示例

```python
exception_counter.Add(1, {"exception_type": "IOError", 'handled_by_user": Trye'})
exception_counter.Add(1, exception_type="IOError", handled_by_user=True)
```

### Asynchronous Counter

异步的 `Counter` 是一个异步的 `Instrument`，在对应的 `Instrument` 被检测时会报告一系列单调递增的值。比如我们会使用异步的 `Counter` 来跟踪下面的指标

- 可以用来报告每个线程、每个处理器或是整个系统的 CPU Time，比如处理器 A 在用户态所花费的以秒为单元的时间
- 每个处理器所产生的 Page Faults

#### Asynchronous Counter Creation

异步的 `Counter` 只能由 `Meter` 来创建，并推荐实现的名称类似为 `ObservableCounter`。用于创建异步 `Counter` 的接口应该接收下面四个参数：

- Name 参数，遵循 `Instrument` 的命名规范
- 可选的 Unit 参数，遵循 `Instrument` 的单元规范
- 可选的 Description 参数，遵循 `Instrument` 的描述规范
- Callback 回调函数

`Callback` 回调函数负责报告所需的指标信息，他只会在 `Meter` 被进行检测的时候调用，具体的 API 需要定义该接口是否是可重入的或是线程安全的。

该回调函数不应该耗费大量的时间，如果多个独立的 SDK 上下文同时共存，他们需要独立的触发这些回调。

`OpenTelemetry API` 的实现者可以从下面两种方式中进行挑选，确定实现方案

- 返回一个列表 *(或是元祖、生成器之类的)* 来代表一系列指标
- 可以使用一个观察者对象作为回调的参数来允许用户独立的设置需要报告的指标信息

我们还建议用户的代码不要在一个回调中，为不同的指标设置相同的属性，如果设置了，`OpenTelemetry SDK` 的实现者会在 SDK 中自己选择如何处理这些指标。比如在一个回调中返回了两个指标，`value = 1, attributes={pid:4, bitness:64}` 以及 `value=2, attributes={pid:4, bitness:64}`，那 SDK 的开发者可能会选择忽略这些指标、选择第一个、选择最后一个、或是其他的处理方式都可能。一个单独的回调结果，会被作为一个独立的观测结果进行处理，比如他们会有一个唯一的时间戳。

下面是该接口的示例

```python
def pf_callback():
  return (
    (8,        ("pid", 0), ("bitness", 64),
    (37741921, ("pid", 4), ("bitness", 64),
    (10465,    ("pid", 880), ("bitness", 32),
  )
     
meter.create_observable_counter(
  name="PF", description="process page faults", pf_callback
)
```

```python
def pf_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(8,        ("pid", 0),   ("bitness", 64))
    result.Observe(37741921, ("pid", 4),   ("bitness", 64))
    result.Observe(10465,    ("pid", 880), ("bitness", 32))

meter.create_observable_counter(
  name="PF", description="process page faults", pf_callback
)
```



#### Asynchronous Counter Operations

异步的 `Counter`只准备用于异步的场景，所以唯一的操作是由初始化时所提供的 `callback` 回调来完成的。



### Histogram

`Histogram ` 是一个同步的 `Instrument`，可以被用来报告特定的数值，这些数值后续可能会被用来做一些有意义的统计分析，他们通常会被用来作为生成直方图  *(Histograms)* 、汇总 *(Summaries)* 或一些百分位 *(percentile)* 信息。比如下面是用 `Histogram` 的几个例子

- 请求的耗时
- 响应消息的大小

#### Histogram Creation

除了 `Meter` 之外不应该有其他的方式来创建 `Histogram`。在 `Meter` 可以用类似 `CreateHistogram`的函数来创建。这个创建的函数必须接收下列这些参数

- `Name` 参数，遵循 `Instrument` 命名规范
- 可选的 `Unit` 参数，遵循 `Instrument`单元命名规范
- 可选的 `Description` 参数，遵循 `Instrument` 描述规范

下面是 `OpenTelemetry API` 作者在实现时可以考虑以下列示例的形式

```python
http_server_duration = meter.create_histogram(
  name="http.server.duration",
  description="measures the duration of the inbound HTTP request",
  unit="millseconds",
  value_type=float
)
```

#### Histogram Operations

##### Record

使用指定的值来更新分析信息。这个接口不应该返回任何的值，它的参数是

- 当前 `Measurement` 指标的值，该值必须是一个非负的值
- 可选的 `Attrubutes` 属性

`OpenTelemetry API` 的作者来选择如何灵活的传递属性，下面是接口的示例

```python
http_server_duration.Record(50, {"http.method": "POST", "http.scheme": "http"})
http_server_duration.Record(100, http_method="GET", http_scheme="http")
```



### Asynchronous Gauge

 `Gauge` 是一个异步的用来报告 `non-additive` 非附加性的值的 `Instrument`，*(比如房间的温度，这个温度对于其他的房间来说是没有意义的， 所以他不会被用来进行累加之类的操作)*。

> 注意，如果这个值是 `additive` 有附加性的，*(比如处理器的堆大小 - 他在用来报告多个处理器中每个处理器的大小并会被累加起来作为总体的堆大小的话)* 那就应该使用 [Asyncronous Counter](#Asynchronous Counter) 或是 [Asynchronous UpDownCounter](#Asynchronous UpDownCounter)。

下面是使用 `Gauge` 的例子

- 当前房间的温度
- CPU 的风扇速度

#### Asynchronous Gauge Creation

异步的 `Gauge` 只能够使用 `Meter` 来创建，他可能是同时使用类似名为 `CreateObservableGauge` 的函数。创建这个对象的函数需要接收下面的参数

- `Name` 参数，遵循 `Instrument` 命名规范
- 可选的 `Unit` 指标，遵循 `Instrument` 单元规范
- 可选的 `Description` ，遵循 `Instrument` 描述规范
- `Callback` 回调函数

回调函数只会在对应的 `Meter` 被进行观察的时候调用，并需要负责报告所需的指标信息，同时这个回调函数不应该花费不确定的大量的时间，如果运行中的运用中有多个独立的 SDK ，他们之间对这个回调函数的调用也应该是独立的。

`OpenTelemetry API` 的作者应该选择下面两种方式之一来实现它

- 返回一个关于 `Measurement` 指标 的列表 *(或是元祖、生成器、迭代器等)*
- 使用一个观察者参数让回调能够独立的报告每个所需的 `Measurement`

用户层面的代码不应该在同一个回调的不同 `Measurement` 指标中提供相同的 `Attributes` 属性，因为 `SDK` 针对这种情况可以选择自己的处理方式，比如在回调中返回了两个指标信息 `value=3.38, attributes={cpu:1, cpu:2}` 以及 `value=3.51, attributes={cpu:1, cpu:2}`，则 `SDK` 可以选择直接将他们传递出去 *(也就是下游的消费者会处理到相同的信息)*，丢弃整个报告信息，取其中最后的那条等等。`API` 需要对观察过程中来自同一个回调的多个指标作为单独的整体进行记录，比如需要为他们记录相同的时间戳。

`API` 应该提供传递某些 `state` 状态给回调的方式，`OpenTelemetry API` 的作者应该自己选择合适的方式。

下面是一些示例

```python
def cpu_frequency_callback():
  # Note: in the real world these would be retrieved from the operating system
  return (
    (3.38, ("cpu", 0), ("core", 0)),
    (3.51, ("cpu", 0), ("core", 1)),    
    (0.57, ("cpu", 1), ("core", 0)),
    (0.56, ("cpu", 1), ("core", 1)),    
  )

meter.create_observable_gauge(
  name="cpu.frequency",
  description="the real-time CPU clock speed",
  callback=cpu_frequency_callback,
  unit="GHz",
  value_type=float
)
```

```python
def cpu_frequency_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(3.38, ("cpu", 0), ("core", 0))
    result.Observe(3.51, ("cpu", 0), ("core", 1))
    result.Observe(0.57, ("cpu", 1), ("core", 0))
    result.Observe(0.56, ("cpu", 1), ("core", 1))

meter.create_observable_gauge(
    name="cpu.frequency",
    description="the real-time CPU clock speed",
    callback=cpu_frequency_callback,
    unit="GHz",
    value_type=float)
```



#### Asynchronous Gauge Operations

异步的 `Gauge` 适用于异步的场景，他唯一提供的操作就是创建 `Gauge` 时所注册的 `callback` 回调函数。



### UpDownCounter

`UpDownCounter` 是一个支持进行递增或递减的同步的 `Instrument`

> 即如果对应的值是单调递增的，则应该使用 [Counter](#Counter)

比如下面是几个使用 `UpDownCounter` 的示例

- 活跃的请求数
- 在队列中的元素数量

`UpDownCounter` 所适合的是具体的值不需要进行预先计算，或是获取当前值时需要付出额外努力的场景，如果预先计算的值已经准备好了，或者是可以很便捷的获取当前值的各个快照，那就应该使用 [Asynchronous UpDownCounter](#Asynchronous Counter) 。

举个获取某个集合的大小作为例子，大部分的编程语言都会提供一个获取集合大小的接口，无论这个接口的功能是直接获取其内部的大小值还是通过某些方式计算出来的，如果这个大小能够直接的从这些接口获取，那就应该使用 [Asynchronous UpDownCounter](#Asynchronous Counter) 了。

```python
items = []
meter.create_observable_up_down_counter(
  name="store.inventory",
  description="the number of the items available",
  callback=lambda result: result.Observe(len(items))
)
```

这里还有一个编程语言运行时的接口无法提供充足信息的例子，比如根据颜色跟材质来报告包裹中的分组数量

| Color  | Material | Count |
| ------ | -------- | ----- |
| Red    | Aluminum | 1     |
| Red    | Steel    | 2     |
| Blue   | Aluminum | 0     |
| Blue   | Steel    | 5     |
| Yellow | Aluminum | 0     |
| Yellow | Steel    | 3     |



```python
items_counter = meter.create_up_down_counter(
    name="store.inventory",
    description="the number of the items available")

def restock_item(color, material):
    inventory.add_item(color=color, material=material)
    items_counter.add(1, {"color": color, "material": material})
    return true

def sell_item(color, material):
    succeeded = inventory.take_item(color=color, material=material)
    if succeeded:
        items_counter.add(-1, {"color": color, "material": material})
    return succeeded
```



#### UpDownCounter Creation

`UpDownCounter` 只能够通过 `Meter` 来进行创建，创建的接口需要接收下列参数

- `Name` 参数，遵循 `Instrument` 命名规范
- 可选的 `Unit` 参数，遵循 `Instrument`单元命名规范
- 可选的 `Description` 参数，遵循 `Instrument` 描述规范

下面是创建 `UpDownCounter` 的示例

```python
scustomers_in_store = meter.create_up_down_counter(
  name="grocery.customers",
  description="measures the current customers in the grocery store",
  value_type=int
)
```

#### UpDownCounter Operations

##### Add

使用指定的值递增或递减 UpDownCounter，这个接口不会返回任何的结果，他接收下面的参数

- 具体需要增加的值，可以是正数也可以是负数或零
- 可选的属性

`OpenTelemetry API` 的作者应该选择灵活的方式来独立的传递属性参数，下面是一个 `OpenTelemetry API` 的可以考虑的方式

```python
customers_in_store.Add(1, {"account.type": "commercial"})
customers_in_store.Add(-1, account_type="residential")
```



### Asynchronous UpDownCounters

异步的 `UpDownCounter` 是一个异步的 `Instrument`，可以在被进行观察的时候报告具有附加性的值 *(比如处理堆的大小，因为报告各个堆的大小，然后求他们的总和来表达堆的整体使用状况是有实际意义的)*。

> 如果值是单调递增的，则应该使用 [Asynchronous Counter](#Asynchronous Counter) ，如果值是不具有附加性的，则应该使用 [Asynchronous Gauge](#Asynchronous Gauge) 。

下面是使用异步的 `UpDownCounter` 的场景示例

- 处理的堆尺寸
- 无锁的循环缓冲区大概的元素数量

#### Asynchonous UpDownCounter Creation

异步的 `UpDownCounter` 允许通过 `Meter` 来进行创建，可能是使用类似 `CreateObservableUpDownCounter` 之类的接口。这个接口应该接收下面的参数

- `Name` 参数，遵循 `Instrument` 命名规范
- 可选的 `Unit` 指标，遵循 `Instrument` 单元规范
- 可选的 `Description` ，遵循 `Instrument` 描述规范
- `Callback` 回调函数

回调函数只会在对应的 `Meter` 被进行观察的时候调用，并需要负责报告所需的指标信息，同时这个回调函数不应该花费不确定的大量的时间，如果运行中的运用中有多个独立的 SDK ，他们之间对这个回调函数的调用也应该是独立的。

`OpenTelemetry API` 的作者应该选择下面两种方式之一来实现它

- 返回一个关于 `Measurement` 指标 的列表 *(或是元祖、生成器、迭代器等)*
- 使用一个观察者参数让回调能够独立的报告每个所需的 `Measurement`

用户层面的代码不应该在同一个回调的不同 `Measurement` 指标中提供相同的 `Attributes` 属性，因为 `SDK` 针对这种情况可以选择自己的处理方式，比如在回调中返回了两个指标信息 `value=1, attributes={pid:4, bitness:64}` and `value=2, attributes={pid:4, bitness:64}`，则 `SDK` 可以选择直接将他们传递出去 *(也就是下游的消费者会处理到相同的信息)*，丢弃整个报告信息，取其中最后的那条等等。`API` 需要对观察过程中来自同一个回调的多个指标作为单独的整体进行记录，比如需要为他们记录相同的时间戳。

`API` 应该提供传递某些 `state` 状态给回调的方式，`OpenTelemetry API` 的作者应该自己选择合适的方式。

下面是接口的示例

```python

def ws_callback():
    # Note: in the real world these would be retrieved from the operating system
    return (
        (8,      ("pid", 0),   ("bitness", 64)),
        (20,     ("pid", 4),   ("bitness", 64)),
        (126032, ("pid", 880), ("bitness", 32)),
    )

meter.create_observable_updowncounter(
    name="process.workingset",
    description="process working set",
    callback=ws_callback,
    unit="kB",
    value_type=int)
```

```python

def ws_callback(result):
    # Note: in the real world these would be retrieved from the operating system
    result.Observe(8,      ("pid", 0),   ("bitness", 64))
    result.Observe(20,     ("pid", 4),   ("bitness", 64))
    result.Observe(126032, ("pid", 880), ("bitness", 32))

meter.create_observable_updowncounter(
    name="process.workingset",
    description="process working set",
    callback=ws_callback,
    unit="kB",
    value_type=int)
```

#### Asynchronous UpDownCounter Operations

异步的 `UpDownCounter` 适用于异步的场景，他唯一提供的操作就是创建 `UpDownCounter` 时所注册的 `callback` 回调函数。

## Measurement

`Measurement` 表示一个通过 指标 `API` 报告给 `SDK` 的数据点，具体的信息可以参考 [Metrics Programming Model](https://opentelemetry.io/docs/reference/specification/metrics/#programming-model) 。简单来说 `Measurements` 可以概括为

- 一个值
- 一系列属性

