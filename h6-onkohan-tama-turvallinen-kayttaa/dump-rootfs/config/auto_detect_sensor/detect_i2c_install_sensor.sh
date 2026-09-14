#!/bin/sh
CONFIG_FILE="/config/auto_detect_sensor/sensor_db.cfg"

set_sensor_std_to_sinfo()
{
	local i2c_slave_addr
	local i2c_clock_name
	local i2c_clock_rate
	local i2c_reg_part_num
	local i2c_addr_len
	local i2c_val_len
	local setting_content

	# 系统中支持的sensor种类
	# sensors=`ls /etc/sensor | awk -F- '{print $1}'`
	sensors=`sed -n '/sensors/'p ${CONFIG_FILE} | awk -F= '{print $2}' | sed 's/,/ /g'`
	for sensor in $sensors
	do
		setting_content="cfginput:"
		# 获取sensor的配置
		for key in slave_addr reg_part_num clock_name clock_rate addr_len val_len
		do
			val=$(awk -F '=' '/\['"$sensor"'\]/{a=1}a==1&&$1~/'"i2c_$key"'/{gsub(/[[:blank:]]*/,"",$2);print $2;exit}' $CONFIG_FILE)

			case $key in
				clock_name)
					i2c_clock_name="$val"
				;;
				slave_addr)
					i2c_slave_addr="$val"
				;;
				reg_part_num)
					i2c_reg_part_num="$val"
				;;
				clock_rate)
					i2c_clock_rate="$val"
				;;
				addr_len)
					i2c_addr_len="$val"
				;;
				val_len)
					i2c_val_len="$val"
				;;
			esac
		done
		setting_content="$setting_content${sensor} ${i2c_slave_addr} ${i2c_addr_len} ${i2c_val_len} ${i2c_clock_name} ${i2c_clock_rate} ${i2c_reg_part_num}"

		sensor_id_part_num=${i2c_reg_part_num}

		if [ $sensor_id_part_num -gt 8 ] || [ $sensor_id_part_num -lt 1 ]; then
			echo Invalid i2c_reg_part_num in ${sensor} config, Please check again
			sensor_id_part_num=0
			return
		fi

		for index in `seq 1 ${sensor_id_part_num}`
		do
			key="reg_${index}_addr"
			val=$(awk -F '=' '/\['"$sensor"'\]/{a=1}a==1&&$1~/'"i2c_$key"'/{gsub(/[[:blank:]]*/,"",$2);print $2;exit}' $CONFIG_FILE)
			i2c_reg_addr="$val"
			key="reg_${index}_val"
			val=$(awk -F '=' '/\['"$sensor"'\]/{a=1}a==1&&$1~/'"i2c_$key"'/{gsub(/[[:blank:]]*/,"",$2);print $2;exit}' $CONFIG_FILE)
			i2c_reg_val="$val"
			setting_content="$setting_content ${i2c_reg_addr} ${i2c_reg_val}"
		done
		# 将sensor信息输入到sinfo.ko驱动
		echo ${setting_content} > /proc/jz/sinfo/info
	done
}

insmod /lib/modules/3.10.14/sinfo.ko

set_sensor_std_to_sinfo

echo 1 >/proc/jz/sinfo/info

sensor_name=`cat /proc/jz/sinfo/info | awk -F: '{print $2}'`

isp_name=${sensor_name}-t31.bin
if [ ! -e /tmp/base-files/cfg/${isp_name} ]; then
	echo "need copy---------------------------------------"
	mkdir -p /tmp/base-files/cfg
	cp -f /etc/default_isp/${isp_name} /tmp/base-files/cfg/${isp_name}
fi

if [ -n "${sensor_name}" ]
then
	echo "========== Sensor ${sensor_name} was detected! ============="
	echo "insmod /config/auto_detect_sensor/modules/sensor_${sensor_name}_t31.ko data_interface=1 shvflip=1"
	insmod /config/auto_detect_sensor/modules/sensor_${sensor_name}_t31.ko data_interface=1 shvflip=1
else
	echo "========== No available sensor! ============="
fi
