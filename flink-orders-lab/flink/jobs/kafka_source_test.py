from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaOffsetsInitializer,
)
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy


env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

source = (
    KafkaSource.builder()
    .set_bootstrap_servers("redpanda:9092")
    .set_topics("orders")
    .set_group_id("flink-orders-lab")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "orders-source",
)

stream.print()

env.execute("redpanda-kafka-source-test")

