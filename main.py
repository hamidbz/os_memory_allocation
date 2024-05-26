import random
import time

def generate_partitions(total_memory, num_partitions):
    partitions = []
    remaining_memory = total_memory
    for _ in range(num_partitions - 1):
        size = random.randint(1, remaining_memory // (num_partitions - len(partitions)))
        partitions.append(size)
        remaining_memory -= size
    partitions.append(remaining_memory)
    return partitions


def allocate_processes1(processes, partitions, total_memory):
    process_list = processes.copy()
    partition_usage = [0] * len(partitions)
    process_allocation = [-1] * len(processes)
    queue = processes.copy()
    where_to_go = [0] * len(processes)
    partition_ramain = partitions.copy()
    memory_utilization = [0]
    process_in_partions = []

    def find(size):
        for i in range(len(partitions)):
            if size <= partition_ramain[i]:
                return i
        return -1
    
    def add():
        for i in range(len(process_allocation)):
            if process_allocation[i] == -1:
                q = find(processes[i]['size'])
                if q != -1 and (processes[i]['size'] <= partition_ramain[q]):
                    process_allocation[i] = q
                    partition_usage[q] += processes[i]['size']
                    partition_ramain[q] -= processes[i]['size']
                    queue.remove(processes[i])
                    process_in_partions.append(processes[i])
        temp = sum(partition_usage) / total_memory * 100
        memory_utilization.append(temp)
    
    def remove(pindex):
        x = process_allocation[pindex]
        size = processes[pindex]['size']
        partition_usage[x] -= size
        partition_ramain[x] += size
        process_in_partions.remove(processes[pindex])
        if queue != []:
            p = queue.pop()
            q = find(p['size'])
            if q != -1 and (p['size'] <= partition_ramain[q]):
                i = processes.index(p)
                process_allocation[i] = q
                partition_usage[q] += p['size']
                partition_ramain[q] -= p['size']
                process_in_partions.append(p)
            else:
                queue.insert(0,p)


    def main():
        use = 0
        cureent = 1
        add()
        while process_list != []:
            p = process_list.pop()
            i = processes.index(p)
            if p in process_in_partions:
                processes[i]['wait'] = cureent
                use += processes[i]['service']
                cureent += processes[i]['service']
                # s = processes[i]['service'] / 10
                # time.sleep(s)
                remove(i)
                cureent += 1
            else:
                process_list.insert(0,p)
                add()
                cureent += 1

        processor_utilization = use / cureent * 100
        return processor_utilization

    processor_utilization = main()
    memory_utilization = max(memory_utilization)
    return process_allocation, memory_utilization, processor_utilization

    
def allocate_processesN(processes, partitions, num_partitions, total_memory):
    process_list = processes.copy()
    partition_usage = [0] * len(partitions)
    process_allocation = [-1] * len(processes)
    queues = [[] for _ in range(num_partitions)]
    process_allocation_queue = process_allocation.copy()
    partition_ramain = partitions.copy()
    memory_utilization = [0]
    process_in_partions = []

    def find(size):
        for i in range(len(partitions)):
            if size <= partitions[i]:
                return i
        return -1
    
    def add():
        for i in range(len(process_allocation)):
            q = find(processes[i]['size'])
            if q != -1:
                if partition_ramain[q] >= processes[i]['size']:
                    process_in_partions.append(processes[i])
                    process_allocation[i] = q
                    partition_ramain[q] -= processes[i]['size']
                    partition_usage[q] += processes[i]['size']
                else:
                    queues[q].append(processes[i])
                    process_allocation_queue[i] = q
                    
        
    def remove(pindex):
        x = process_allocation[pindex]
        process_in_partions.remove(processes[pindex])
        size = processes[pindex]['size']
        partition_usage[x] -= size
        partition_ramain[x] += size
        if queues[x] != []:
            p = queues[x].pop()
            if partition_ramain[x] >= p['size']:
                i = processes.index(p)
                process_in_partions.append(p)
                process_allocation[i] = x
                partition_ramain[x] -= p['size']
                partition_usage[x] += p['size']
                temp = sum(partition_usage) / total_memory * 100
                memory_utilization.append(temp)
            else:
                queues[x].insert(0, p)

    def main():
        use = 0
        cureent = 1
        add()
        while process_list != []:
            p = process_list.pop()
            idx = processes.index(p)
            if p in process_in_partions:
                p['wait'] = cureent
                cureent += p['service']
                use += p['service']
                # time.sleep(0.1 * p['service'])
                remove(idx)
                cureent += 1
            else:
                process_list.insert(0, p)
                cureent += 1  

        processor_utilization = use / cureent * 100
        return processor_utilization                

    processor_utilization = main()
    memory_utilization = max(memory_utilization)
    return process_allocation, memory_utilization, processor_utilization


def main():
    total_memory = int(input("Memory Size: "))

    num_partitions = int(input("Number Of Partitions: "))

    num_processes = int(input("Number Of Processes: "))
    partitions = generate_partitions(total_memory, num_partitions)
    print("Partion sizes:")
    for i, size in enumerate(partitions):
        print(f"Partion {i}: {size}kbyte")

    print('\n-------------------------\n')

    processes = [{'id': i, 'size': random.randint(1, max(partitions) // 2), 'service': random.randint(1,3), 'wait': None} for i in range(num_processes)]
    print("Processes:")
    for process in processes:
        print(f"Process {process['id']} with size {process['size']}kbyte.")
    
    print('\n-------------------------\n')

    print("Using Multipile queues:")
    process_allocation, memory_utilization, processor_utilization = allocate_processesN(processes, partitions, num_partitions, total_memory)
    print("Asigments:")
    for i, allocation in enumerate(process_allocation):
        print(f"Process {i} with waiting time {processes[i]['wait']} and service time {processes[i]['service']} assigned to partition {allocation}.")
    
    print('\n------------Using Multipile queues-------------\n')
    print(f'Maximum memory utilization is: {memory_utilization}%')
    print(f'Processor utilization is: {processor_utilization}%')    

    print('\n-------------------------\n')

    print("Using single queues:")
    process_allocation, memory_utilization, processor_utilization = allocate_processes1(processes, partitions, total_memory)
    print("Asigments:")
    for i, allocation in enumerate(process_allocation):
        print(f"Process {i} with waiting time {processes[i]['wait']} and service time {processes[i]['service']} assigned to partition {allocation}.")
    
    print('\n------------Using single queues-------------\n')
    print(f'Maximum memory utilization is: {memory_utilization}%')
    print(f'Processor utilization is: {processor_utilization}%')

    


main()
    
