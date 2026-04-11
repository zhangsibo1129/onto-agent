#!/bin/bash
# 初始化 Fuseki 数据集

echo "初始化 Fuseki onto-agent 数据集..."

# 检查 Fuseki 是否运行
if ! curl -s http://localhost:3030/$/ping > /dev/null 2>&1; then
    echo "错误: Fuseki 服务未运行"
    exit 1
fi

# 检查数据集是否已存在
RESPONSE=$(curl -s "http://localhost:3030/onto-agent/sparql?query=SELECT+*+WHERE+{?s+?p+?o}+LIMIT+1" 2>&1)
if echo "$RESPONSE" | grep -q "404"; then
    echo "数据集不存在，创建中..."
    
    # 创建持久化 TDB 数据集
    curl -X POST "http://localhost:3030/$/datasets" \
      -H "Content-Type: application/json" \
      -d '{"datasetName": "onto-agent", "persistent": true, "dbType": "tdb"}' \
      2>/dev/null
      
    sleep 2
    
    # 再次检查
    RESPONSE=$(curl -s "http://localhost:3030/onto-agent/sparql?query=SELECT+*+WHERE+{?s+?p+?o}+LIMIT+1" 2>&1)
    if echo "$RESPONSE" | grep -q "404"; then
        echo "创建失败，尝试内存模式..."
        
        # 尝试创建内存数据集
        curl -X POST "http://localhost:3030/$/datasets" \
          -H "Content-Type: application/json" \
          -d '{"datasetName": "onto-agent", "persistent": false, "dbType": "mem"}' \
          2>/dev/null
          
        sleep 2
    fi
else
    echo "数据集已存在"
fi

# 验证
FINAL=$(curl -s "http://localhost:3030/onto-agent/sparql?query=SELECT+*+WHERE+{?s+?p+?o}+LIMIT+1&format=json" 2>&1)
if echo "$FINAL" | grep -q "results"; then
    echo "✓ 数据集 onto-agent 已就绪"
elif echo "$FINAL" | grep -q "JSON"; then
    echo "✓ 数据集 onto-agent 已就绪（空结果集）"
else
    echo "✗ 数据集创建可能失败，当前响应: $FINAL"
fi
