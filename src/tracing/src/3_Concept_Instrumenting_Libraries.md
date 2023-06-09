# 3. Concept - Instrumenting Libraries

`OpenTelemetry` 为许多的库提供了自动记录的仪表功能，他们通常都是通过一些库的 `Hook` 或者是 `Monkey-Patching` 等方式来完成的。

`OpenTelemetry` 的原生仪表库提供了更好的可观察性跟开发体验，移除对库的依赖跟暴露出记录的 Hook:

- 自定义的日志 Hook 可以使用通用且易于使用的 `OpenTelemetry API` 来替代，用户只需要跟 `OpenTelemetry` 进行交互
- `Trace`、`Log`、`Metric` 等程序中的信息会具有更好的关联性跟可靠
- 一致的约定能够让用户在使用不同的技术或编程语言时得到相近的体验
- `Telemetry Signal` 作为扩展点，可以用于在不同的场景中提供对数据进行微调 *(比如 Filtered、Processed、Aggregated)* 的支持

## Semantic Conventions

现在可用的 [Semantic Conventions][1] 语义约定涵盖了 `Web-Frameworks`、`RPC 客户端`、`数据库`、`消息传递客户端`还有其他更多的定义。

如果你的库是其中的一种 - 就遵守对应的约定，他们描述了正确的来源并可以此来确定应该在对应的 `Span`  中附加哪些信息。预定可以让仪表信息更加统一：负责处理仪表数据的人可以在不需要学习库的特定细节，可视化的提供者也可以为各种技术提供支持 *(比如数据库或消息系统)* 。当各个库都遵守约定时，许多的使用场景就可以在无需用户在进行配置的情况下来使用了。

欢迎你来添加新的约定，[Instrumentation Slack][2] 跟 [Specification Repo][3] 都可以是你的起点。

## When **NOT** to instrument

有一些库可能只是对网络调用做了一层浅浅的封装，重点在于 `OpenTelemetry` 具有为底层的 `RPC`  调用自动记录仪表信息的功能，在这个情况下，库的仪表记录功能是不必要的：。

如果是下列的情况，**不要**记录仪表信息：

- 你的库是一些位于顶层的自描述接口的一个轻量代理
- *OpenTelemtery* 为底层的网络调用记录了仪表信息
- 你的库没办法为对应的约定填充合适的信息

如果不够确定，那就不要记录，你可以把他放到你确定需要的时候再来做这个事情。

尽管选择了不记录仪表信息，为你的内部 RPC 客户端实例提供一个配置 `OpenTelemetry` 处理器的能力也是好的。这对于那些没有完全支持自动记录仪表信息的语言来说，仍然是有用的。

剩余的文档则是介绍了当你想记录仪表信息时，应该如何做。

## OpenTelemetry API

首先是要添加依赖 *OpenTelemtry API* 所需的包。

`OpenTelemetry` 有两个主要的模块 - `API` 以及 `SDK`。`OpenTelemetry API` 是系列操作的抽象而不是实现。除非为应用再添加 `OpenTelemetry SDK` ，否则的话你的应用并不会记录任何东西，也不会对性能产生影响。

### Libraries should only use OpenTelemetry API

你可能会理所当然的对添加新的依赖产生担忧，在这里我们会提供一些考量来帮助你如何最小化依赖所产生的 `Dependency Hell`：

- `OpenTelemetry Trace API` 在 2021 年初期就实现了稳定，他也会遵循 [Semantic Versioning 2.0][4]  的语义来仔细的保持 API 的稳定性
- 在选择依赖时，使用最早的稳定版本的 `OpenTelemetry API (1.0.*)` 以及避免在不需要使用到新的 `Feature` 时进行升级
- 在你的仪表信息稳定时，考虑将它实现为一个独立的包：他不会对没使用到的地方产生任何影响。你可以将它保留在你的仓库也可以把他贡献给 `OpenTelemetry` 让他能够跟其他的仪表盘一起提供给他人使用
- 语义化的约定当前还没稳定，他不会导致任何功能上的问题，但你可能会需要每个一段时间更新一下。在预览插件或是将它保留在 `OpenTelemetry` 的其他仓库并不会造成什么破坏



### Getting a tracer

所有应用程序的配置都会被隐藏在库里的 `Tracer API` 里，这些库在默认的情况下，应该从全局的 `TracerProvider` 中获取。

```java
private static final Tracer tracer = GlobalOpenTelemetry.getTracer("demo-db-client", "0.1.0-beta");
```

为这些库提供一个接口允许应用传递一个明确的 `TracerProvider` 有助于更好的实现依赖注入及简化测试。

在使用你的库获取 `Tracer` 时提供指定的名称跟版本，他们会在遥测的数据上体现并能够帮助用户使用他们来对数据进行过滤、明确数据的具体来源，并以此来进行调试。

## What to instrument

![image-20211020102106594](./3. Concept - Instrumenting Libraries.assets/image-20211020102106594.png)

### Public API

开放的接口是非常合适监测的候选人：为开放接口创建的 `Span` 能够帮助用户将他们跟具体的应用代码建立关联，明确接口所调用的耗时跟结果。那哪些接口是应该监测的呢

- 公开的、会在函数内部发起网络调用的、或是所需的本地需要花费大量时间或可能会失败的操作 *(比如 IO 操作)*
- 用于处理请求或者是消息的

#### Instrumentation example:

```java
private static final Tracer tracer = GlobalOpenTelemetry.getTracer("demo-db-client", "0.1.0-beta");

private Response selectWithTracing(Query query) {
	// check out conventions for guidance on span names and attributes
  Span span = tracer.spanBuilder(String.format("SELECT %s.%s", dbName, collectionName))
    .setSpanKind(SpanKind.CLIENT)
    .setAttribute("db.name", dbName)
    // ...
    .startSpan();
  
  // makes span active and allows correlating logs and nest spans
  try (Scope unused = span.makeCurrent()) {
    Response response = query.runWithRetries();
    if (response.isSuccessful()) {
      span.setStatus(StatusCode.OK);
    }
    if (span.isRecording()) {
    	// populate reponse attributes for reponse codes and other information
    }    
  } catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR, e.getClass().getSimpleName());
    throw e;
  } finally {
    span.end();
  }
}
```

要严格遵守约定中需要填充的属性，如果没有可以填充的，则检查一下 [通常的约定][5]。

### Nested network and other spans

网络的调用通常会被 `OpenTelemetry` 的自动仪表库中对应的客户端实现进行跟踪。

如果 `OpenTelemetry` 还不支持跟踪你的网络客户端，就需要你自己来做出最好的决定了，下面的列表可能有助于你做出决定

- 跟踪网络的调用是否会提高用户的可观察性或是提供其他能够帮助用户的能力？
- 你的库是不是对最顶层的公开的文档化的接口的包装？如果出现问题，用户需不需要获得底层服务的支持？
  - 如果是则进行跟踪确保跟踪每个独立的网络尝试
- 跟踪这些信息会不会是 `Span` 变得冗长？或是会否对性能产生影响？
  - 使用日志或 `Span Event` 来处理冗长的信息。日志可以关联到父 `Span` *(即公开的接口)*  上，`Span Event` 也可以设置到公开接口的 `Span` 上
  - 如果他们需要成为 `Span` *(比如为了作为独立的 Trace Context 进行传播)*，将他们放到配置的选项中并默认将其关闭

如果 `OpenTelemtry` 已经支持跟踪你的网络调用，，你应该不需要在做重复的事情了，但也有下面的一些例外：

- 为没有使用自动仪表功能的用户提供支持 *(比如没有明确的运行环境或是对 Monkey-Paching 比较在的用户)*
- 需要为底层的服务启用自定义的关联信息跟上下文传播协议
- 需要为某些自动仪表库没有完全覆盖到的库或服务填充 `Span` 信息

<u>WARNING:</u> 通用的用来避免重复的解决方案还在实现中

### Events

`Trace` 是你唯一需要提交的信息，`Event` 跟 `Log` 跟 `Trace` 是相互补充的，他们并不是相同重复的概念。通常来说，如果某些信息有可能会比较冗长，那他就更适合使用 `Log` 来体现，而不是 `Trace`。

如果你的库使用了日志库或是其他的一些类似的机制，检查 [OpenTelemetry Registry](https://opentelemetry.io/registry/) 是否已经将其进行过整合了。整合通常指将当前活跃的 `Trace Context` 信息添加到所有的日志里，因此用户可以将这些信息进行关联。

如果你使用的编程语言跟环境没有通用的日志库，那就使用 `Span Event`  来体现那些需要提供给用户的额外的附加信息，在你想要添加 `Attribute` 的时候使用  `Event` 可能也会更加方便。

最后总结的规则是，使用 `Event` 或 `Log` 来替代 `Span` 记录那些可能会很冗长的信息。使用你当前持有的 `Span` 实例来添加 `Event`，在可能的情况下避免使用当前激活的 `Span`，因为你并不知道还有哪些其他的控制代码对其进行了引用。



## Context Propagation

### Extract Context

如果你处理的是基础的设施或是一个会接收上游请求的库，比如 `Web Framework` 或是 `Messaging Consumer`，你需要从到达的 请求或消息中提取所需的上下文。`OpenTelemetry` 提供了 `Propagator API` 用来隐藏特定的传播标准及从线路中读取 `Trace Context`。

在一个单独的响应中，只会在线路中读取出一个上下文信息，并会将它作为新 `Span` 的父节点。

在创建了新的 `Span` 后，你应该将其设置为激活的状态并尽可能明确的传递新的上下文给应用代码 *(通过回调或是处理函数)*。

```java
// Extract the context
Context extractedContext = propagator.extract(Context.current(), httpExchange, getter);
Span span = tracer.spanBuider("receiver")
  .setSpanKind(SpanKind.SERVER)
  .setParent(extractedContext)
  .startSpan();

// make span active so any nested telemetry is correlated
try (Scope unused = span.makeCurrent()) {
  userCode();
} catch (Exception e) {
  span.recordException(e);
  span.setStatus(StatusCode.ERROR);
  throw e;
} finally {
  span.end();
}
```

这里还有一个完整的 [Java 提取上下文](https://opentelemetry.io/docs/java/manual_instrumentation/#context-propagation) 的例子，其他编程语言的可以查看 `OpenTelemetry` 相关的文档。

在处理消息系统时，可能会一次收到超过一条的消息，这些消息可以通过 [Links](https://opentelemetry.io/docs/java/manual_instrumentation/#create-spans-with-links) 整合到一个 `Span`，具体的可以参照 [Message Conventions](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/messaging.md)。

<u>WARN:</u> 这部分内容还处于建设中。

### Injecting Context

当你要往外发送一个调用时，通常会需要将一些上下文信息传递给下游的服务。可以用 `Propagator API` 来创建一个新的 `Span` ，来将上下文注入到对外的调用消息里。可能还会有其他的一些场景需要用不同的方式来注入上下文，比如当你需要创建消息提供给异步的处理。

```java
Span span = tracer.spanBuilder("send")
  .setSpanKind(SpanKind.CLIENT)
  .startSpan();

// make span active so any nested telemetry is corrlated
// even network calls might have nested layers of spans, log or events
try (Scope unused = span.makeCurrent()) {
  // inject the context
  propagator.inject(Context.current(), transportLayer, setter);
  send();
} catch (Exception e) {
  span.recordException(e);
  span.setStatus(StatusCode.ERROR);
  throw e;
} finally {
  span.end();
}
```

当然也可能会有例外：

- 下游的服务不支持元数据或禁止接收未知的字段
- 下游的服务未定义关联的协议，服务未来的某个版本是否会开始支持上下文的传递，那就注入吧！
- 下游的服务支持自定义的关联协议
  - 尽力去兼容自定义的传播器：在可以的情况下使用 `OpenTelemetry` 的 `Trace Context`
  - 或是在 `Span` 上生成跟添加自定义的关联 ID 信息

### In-process

- **激活你使用的 `Span`** *(即成为 current)* : 这样才能启用 `Span` 跟 `Log` 以及其他嵌套的自动仪表信息
- 如果库有 `Context` 的概念，支持 **额外** 的更具体的 `Trace Context` 加入当前的 `Span`
  - 将 `Span` 添加到库的上下文中，并写明文档如何去使用他
  - 允许用户在你的上下文中传递 `Trace Context`
- 在库中明确的传递 `Trace Context` - 因为当前的活跃 `Span` 在回调中可能会发生改变
  - 尽快的从公开接口中捕获活跃的上下文，然后将它作为自身 `Span` 的父级上下文来使用
  - 使用明确的实例来传递上下文并在其之上记录 `Attribute`、`Exeception`、``Event`等信息
  - 这些都是必须的，如果你启动了一个线程在后台处理或是其他的一些异步的操作都可能会对上下文产生影响，但具体的限制还得看具体的编程语言

## Metrics

[Metric API](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md) 当前还未稳定，并且我们还未完成对 `Metric` 约定的定义。

## Misc

### Instrumentation Registry

请将你的仪表库添加到 [OpenTelemetry Registry](https://opentelemetry.io/registry/) 让更多其他的用户能够使用。

### Performance

`OpenTelemetry API` 在没有引入 `SDK` 的情况下并不会做任何操作。当 `OpenTelemetry SDK` 配置完成后，他也只会 [耗费有限的资源](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/performance.md)。

在现实的应用中，特别是大规模的应用，通常会使用基于 Head-base 进行采样。抽样中的 `Span` 信息的成本应该是较低的，因此你应该检查 `Span` 是否处于 Recoding 状态，以此来避免在填充 `Attribute` 时产生额外的分配以及进行潜在的代价高昂的计算。

```java
// some attribute are important for sampling, they should be provided at creation time
Span span = trace.spanBuilder(String.format("SELECT %s.%s", dbName, collectionName))
  .setSpanKind(SpanKind.CLIENT)
  .setAttribute("db.name", dbName)
  // ...
  .startSpan();

// other attributes, especially those that are expensive to calculate
// should be added if span is recoding
if (span.isRecording()) {
  span.setAttribute("db.statement", sanitize(query.statement()));
}
```

> 简单来说就是确认当前的 `Span` 被采样及进行记录的前提下，才去计算复杂的 `Attribute`

### Error handling

`OpenTelemetry API` 在[运行时中是宽容的](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/error-handling.md#basic-error-handling-principles) - 他不会因为不合法的参数出错，不会抛出异常，会把出现的异常给隐藏起来。这样的话仪表库的问题就不会对应用的逻辑产生任何影响。

### Testing

因为 `OpenTelemetry` 具有多种多样的自动化仪表采集，因此了解仪表库是如何跟其他的遥测数据交互是非常有用的：比如跟到达的请求、发出的请求、日志等。用一个使用了流行的框架跟库来实现的并启用了所有跟踪功能的应用，来测试你的仪表库，然后检查那些与你类似的库是如何使用的。

为了进行单元测试，你可以对 `SpanProcessor` 跟 `SpanExporter` 进行 Mock

```java
@Test
public void checkInstrumentation() {
  SpanExporter exporter = new TestExporter();
  Tracer tracer = OpenTelemetrySdk.builder()
    .setTraceProvider(
    	SdkTracerProvider.builder()
    		.addSpanProcessor(SimpleSpanProcessor.create(exporter))
    		.build()
      ).build()
    .getTracer("test");
}

class TestExporter implements SpanExporter {
  public final List<SpanData> exportedSpans = Collections.synchronizedList(new ArrayList<>());
  
  @Override
  public CompletableResultCode export(Collection<SpanData> spans) {
    exportedSpans.addAll(spans);
    return CompletableResultCode.ofSuccess();
  }
}
```



[1]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/README.md
[2]:	https://cloud-native.slack.com/archives/C01QZFGMLQ7
[3]:	https://github.com/open-telemetry/opentelemetry-specification
[4]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/versioning-and-stability.md
[5]:	https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/span-general.md