# 6. Collector - Getting Started

请先回顾下 [Data Collection Documentation][1] 确保能理解 `OpenTelemetry`中 `Collector` 的部署模型、组件跟适用的仓库。

## Deployment

`OpenTelemetry Collector` 包含一个独立的二进制文件以及提供了两种主要的部署方式

- **Agent**: `Collector` 的实例会更应用一起运行或是在同一个主机上运行 *(比如二进制文件、SideCar、Daemon set)
- **Gateway**: 通常来说为每个集群、数据中心或区域中，将一个或多个 `Collector` 的实例作为独立运行的服务 *(比如是一个 Container 或是一个 Deployment)* 进行部署。

### Agent

我们会推荐在每个主机中以 Agent 的形式部署到对应的环境中。这样的话，Agent 就可以拦截所有接收的遥测数据 *(包括 Pull 跟 Push 两种)*，同样也可以为这些遥测数据添加更具体的元数据，比如自定义的标签或是基础设施的信息。另外，Agent 也可以无需去负责类似客户端所需要做的类似批量处理、重试、加密、压缩等操作。`OpenTelemetry` 仪表库默认情况下会假设本地的 `Collector` 是就绪的并将数据导出。

### Gateway

另外一种是作为网关集群部署到每个集群、数据中心或地区，网关集群会作为独立的服务因此他相对于 Agent 这种基于采样的模式，能够提供更加强大的能力。另外，网关集群还可以限制发送数据的出站点的数量及进行 API Token 的统一管理。每个集群中的 `Collector` 实例都能够独立处理数据，因此能够很容易的使用负载均衡器针对性能所需来进行扩展。在网关集群部署之后，他通常就会开始接收从 Agent 发过来的信息了。



## Getting Started

### Demo

Demo 会部署负载生成器、Agent 跟网关以及 Jaeger、ZipKin 跟 Prometheus 作为后端。更多的信息可以从 Demo 的 [README.md][2] 了解。

```bash
$ git clonet git@github.com:open-telemetry/opentelemetry-collector-contrib.git; \
	cd opentelemetry-collector-contrib/examples/demo; \
	docker-compose up -d
```

### Docker

每个 `Collector` 版本都会发布到 Docker Hub 并附带默认的配置文件

```bash
$ docker run otel/opentelemetry-collector
```

还可以使用他提供的示例，这个示例会使用 Docker Container 启动一个 `Collector` 的 Core 版本，启用所有的 `Receiver`，并将所有的数据导出到本地的文件中。发送到容器的数据会从中提取出所需的 Prometheus 指标。

```bash
$ git clone git@github.com:open-telemetry/opentelemetry-collector.git; \
	cd opentelemetry-collector/examples; \
	go build main.go; ./main & pid1="$!";
	docker run -- rm -p 13133:13133 -p 14250:14250 -p 14268:14268 \
	-p 55678-55679:55678-55679 -p 4317:4317 -p 8888:8888 -p 9411:9411 \
	-v "${PWD}/otel-local-config.yaml":/otel-local-config.yaml \
	--name otecol otel/opentelemetry-collector \
	--config otel-local-config.yaml; \
	kill $pid1; docker stop otelcol
```



### Kubernetes

部署了一个类型为 Deamonset 的 Agent ，以及一个独立的网关实例

```bash
$ kubectl apply -f https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector/main/examples/k8s/otel-config.yaml
```

上例只是作为一个起点的示范，在上实际的生产环境之前需要在进行自定义的配置。

`OpenTelemetry Operator` 可以用来提供管理 `OpenTelemetry Collector` 实例的工具，通过他的类似自动升级处理的功能，能够实现基于 `OpenTelemetry` 配置的服务配置，跟自动进行 SideCar 的配置注入等等。



### Nomad

Reference job files to deploy the Collector as an agent, gateway and in the full demo can be found athttps://github.com/hashicorp/nomad-open-telemetry-getting-started.

### Linux Packaging

Every Collector release includes DEB and RPM packaging for Linux amd64/arm64 systems. The packaging includes a default configuration that can be found at `/etc/otel-collector/config.yaml` post-installation.

> Please note that systemd is require for automatic service configuration

To get started on Debian systems run the following replacing `v0.20.0` with the version of the Collector you wish to run and `amd64` with the appropriate architecture.

```bash
$ sudo apt-get update
$ sudo apt-get -y install wget systemctl
$ wget https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.20.0/otel-collector_0.20.0_amd64.deb
$ dpkg -i otel-collector_0.20.0_amd64.deb
```

To get started on Red Hat systems run the following replacing `v0.20.0` with the version of the Collector you wish to run and `x86_64` with the appropriate architecture.

```bash
$ sudo yum update
$ sudo yum -y install wget systemctl
$ wget https://github.com/open-telemetry/opentelemetry-collector/releases/download/v0.20.0/otel-collector_0.20.0-1_x86_64.rpm
$ rpm -ivh otel-collector_0.20.0-1_x86_64.rpm
```

By default, the `otel-collector` systemd service will be started with the `--config=/etc/otel-collector/config.yaml` option after installation. To customize these options, modify the `OTELCOL_OPTIONS` variable in the `/etc/otel-collector/otel-collector.conf` systemd environment file with the appropriate command-line options (run `/usr/bin/otelcol --help` to see all available options). Additional environment variables can also be passed to the `otel-collector` service by adding them to this file.

If either the Collector configuration file or `/etc/otel-collector/otel-collector.conf` are modified, restart the`otel-collector` service to apply the changes by running:

```bash
$ sudo systemctl restart otel-collector
```

To check the output from the `otel-collector` service, run:

```bash
$ sudo journalctl -u otel-collector
```

### Windows Packaging

Every Collector release includes EXE and MSI packaging for Windows amd64 systems. The MSI packaging includes a default configuration that can be found at `\Program Files\OpenTelemetry Collector\config.yaml`.

> Please note the Collector service is not automatically started

The easiest way to get started is to double-click the MSI package and follow the wizard. Silent installation is also available.

### Local

Builds the latest version of the collector based on the local operating system, runs the binary with all receivers enabled and exports all the data it receives locally to a file. Data is sent to the container and the container scrapes its own Prometheus metrics.

```bash
$ git clone git@github.com:open-telemetry/opentelemetry-collector-contrib.git; \
    cd opentelemetry-collector-contrib/examples/demo; \
    go build client/main.go; ./client/main & pid1="$!"; \
    go build server/main.go; ./server/main & pid2="$!"; \

$ git clone git@github.com:open-telemetry/opentelemetry-collector.git; \
    cd opentelemetry-collector; make install-tools; make otelcol; \
    ./bin/otelcol_$(go env GOOS)_$(go env GOARCH) --config ./examples/local/otel-config.yaml; kill $pid1; kill $pid2
```

[1]:	https://opentelemetry.io/docs/concepts/data-collection
[2]:	https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/examples/demo