HOST=`hostname | awk -F '.xx.com' '{print $1}'`

BrokerId=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/BrokerId | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

TotalEnqueueCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalEnqueueCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')


TotalDequeueCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalDequeueCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')


TotalConsumerCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalConsumerCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

TotalMessageCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalMessageCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

TotalConnectionsCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalConnectionsCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

TotalProducerCount=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/TotalProducerCount | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')


MemoryLimit=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/MemoryLimit | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')


MemoryPercentUsage=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/MemoryPercentUsage | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

StoreLimit=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/StoreLimit | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

StorePercentUsage=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST/StorePercentUsage | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

CurrentStatus=$(curl -u admin:admin -s $HOST:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=broker_$HOST,service=Health/CurrentStatus | grep 200 | awk -F 'value":' '{print $2}' | awk -F ',' '{print $1}')

echo "BrokerId:" $BrokerId
echo "TotalEnqueueCount:" $TotalEnqueueCount
echo "TotalDequeueCount:" $TotalDequeueCount
echo "TotalConsumerCount:" $TotalConsumerCount
echo "TotalMessageCount:" $TotalMessageCount
echo "TotalConnectionsCount:" $TotalConnectionsCount
echo "TotalProducerCount:" $TotalProducerCount
echo "MemoryLimit:" $MemoryLimit
echo "MemoryPercentUsage:" $MemoryPercentUsage
echo "StoreLimit:" $StoreLimit
echo "StorePercentUsage:" $StorePercentUsage
