import csv
from geopy.distance import distance

# 距离阈值
THRESHOLD = 1.0  # 单位为千米

coord_dict = {}
input_file = 'landmarks.csv'
with open(input_file, 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # 获取标题行

    # 遍历csv文件，提取IPv6地址作为哈希列表的key，
    # 将相同key的不同行中经纬度坐标和第三列偏移量存储在字典中
    for row in csv_reader:
        ipv6_address = row[0]
        lat, lon = float(row[3]), float(row[4])
        offset = int(row[2]) if row[2] else None  # 检查第三列是否存在
        improved = row[5]
        if ipv6_address in coord_dict:
            coord_dict[ipv6_address].append((lat, lon, offset, improved))
        else:
            coord_dict[ipv6_address] = [(lat, lon, offset, improved)]

# 对同一IP的不同经纬度坐标间计算距离，对距离小于1km的坐标聚类
cluster_dict = {}
for ipv6_address in coord_dict:
    coords_list = coord_dict[ipv6_address]
    clusters = []
    while coords_list:
        current_coord = coords_list.pop(0)
        current_cluster = [current_coord]
        for coord in coords_list:
            if distance(current_coord[:2], coord[:2]).km <= THRESHOLD:
                current_cluster.append(coord)
        for coord in current_cluster:
            if coord in coords_list:
                coords_list.remove(coord)
        clusters.append(current_cluster)
    cluster_dict[ipv6_address] = clusters

# 获取每个IP地址对应聚类中元素最多、且偏移量绝对值之和最小的簇
max_clusters = {}
for ipv6_address in cluster_dict:
    candidates = cluster_dict[ipv6_address]
    max_count = 0
    min_offset_sum = float('inf')
    for cluster in candidates:
        if 0 in [i[2] for i in cluster]:          #优先选择包含offset = 0的簇
            max_cluster = cluster
            break
        count = len(cluster)
        offsets = [abs(coords[2]) for coords in cluster if coords[2] is not None]
        offset_sum = sum(offsets)
        if count > max_count or (count == max_count and offset_sum < min_offset_sum):
            max_count = count
            min_offset_sum = offset_sum
            max_cluster = cluster
    max_clusters[ipv6_address] = max_cluster

# 输出文件，包含每个IP地址对应聚类中元素最多、且偏移量绝对值之和最小的行
with open('landmarks__filtered.csv', 'w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(header)  # 写入标题行
    with open(input_file, 'r') as input_file:
        csv_reader = csv.reader(input_file)
        next(csv_reader)  # 跳过标题行
        for row in csv_reader:
            ipv6_address = row[0]
            offset = int(row[2]) if row[2] else None
            if offset in [i[2] for i in max_clusters[ipv6_address]]:
                csv_writer.writerow(row)