
# ===== P4 ====
build_p4:
	mkdir -p p4/build
	p4c-bm2-ss -o p4/build/main.json p4/bmv2/main.p4 

run_p4:
	sudo python3 ../network/net.py network/topo_p4.json

# build + run = buran :)
buran_p4: build_p4 run_p4

# ==== DPDK ====

updateDocker:
	sudo docker build -t dpdk_median dpdk

buildDocker:
	sudo docker build -t basis ../docker_basis
	sudo docker build -t dpdk_median dpdk

run_dpdk:
	sudo python3 ../network/net.py network/topo_dpdk.json

buran_dpdk: updateDocker run_dpdk

# ==== Test ====

create_flow:
	python3 host/create_flow.py $(vals)

add_value:
	python3 host/add_value.py $(key) $(val)

get_result:
	python3 host/get_result.py $(key) 

remove_flow:
	python3 host/remove_flow.py $(key)

# ==== General ==
clean:
	rm -r p4/build 2>/dev/null || true
