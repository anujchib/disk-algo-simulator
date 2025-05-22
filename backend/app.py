from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def fcfs(requests, head):
    sequence = [head] + requests
    total_seek = sum(abs(sequence[i] - sequence[i - 1]) for i in range(1, len(sequence)))
    return sequence, total_seek

def sstf(requests, head):
    requests = requests[:]
    sequence = [head]
    total_seek = 0
    while requests:
        closest = min(requests, key=lambda x: abs(x - head))
        total_seek += abs(closest - head)
        head = closest
        sequence.append(head)
        requests.remove(closest)
    return sequence, total_seek

def scan(requests, head, cylinders, direction='left'):
    sequence = [head]
    total_seek = 0
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])

    if direction == 'left':
        for r in left:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if left:
            total_seek += abs(head - 0)
            head = 0
            sequence.append(head)
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    else:
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if right:
            total_seek += abs(cylinders - 1 - head)
            head = cylinders - 1
            sequence.append(head)
        for r in left:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    return sequence, total_seek

def cscan(requests, head, cylinders, direction='left'):
    sequence = [head]
    total_seek = 0
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    if direction == 'left':
        for r in reversed(left):
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if left:
            total_seek += abs(head - 0)
            head = cylinders - 1
            sequence.append(0)
            sequence.append(head)
        for r in reversed(right):
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    else:
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if right:
            total_seek += abs(head - (cylinders - 1))
            head = 0
            sequence.append(cylinders - 1)
            sequence.append(head)
        for r in left:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    return sequence, total_seek

def look(requests, head, direction='left'):
    sequence = [head]
    total_seek = 0
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])

    if direction == 'left':
        for r in left:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    else:
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        for r in left:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    return sequence, total_seek

def clook(requests, head, direction='left'):
    sequence = [head]
    total_seek = 0
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    if direction == 'left':
        for r in reversed(left):
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if right:
            total_seek += abs(head - right[-1])
            head = right[-1]
            sequence.append(head)
        for r in reversed(right[:-1]):
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    else:
        for r in right:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
        if left:
            total_seek += abs(head - left[0])
            head = left[0]
            sequence.append(head)
        for r in left[1:]:
            total_seek += abs(head - r)
            head = r
            sequence.append(head)
    return sequence, total_seek

@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.get_json()

    try:
        requests = list(map(int, data['requests'].split(',')))
        head = int(data['head'])
        cylinders = int(data['cylinders'])
        algorithm = data['algorithm']
        direction = data.get('direction', 'left')
        compare = data.get('compare', False)
    except:
        return jsonify({'error': 'Invalid input format.'})

    def run_algo(algo):
        if algo == 'FCFS':
            return fcfs(requests, head)
        elif algo == 'SSTF':
            return sstf(requests, head)
        elif algo == 'SCAN':
            return scan(requests, head, cylinders, direction)
        elif algo == 'LOOK':
            return look(requests, head, direction)
        elif algo == 'C-SCAN':
            return cscan(requests, head, cylinders, direction)
        elif algo == 'C-LOOK':
            return clook(requests, head, direction)
        else:
            return None, None

    sequence, total_seek = run_algo(algorithm)
    if sequence is None:
        return jsonify({'error': 'Invalid algorithm selected.'})

    result = {
        'sequence': sequence,
        'total_seek': total_seek
    }

    if compare:
        algorithms = ['FCFS', 'SSTF', 'SCAN', 'LOOK', 'C-SCAN', 'C-LOOK']
        all_results = {}
        best_algo = algorithm
        best_seek = total_seek

        for algo in algorithms:
            seq, seek = run_algo(algo)
            if seq:
                all_results[algo] = seek
                if seek < best_seek:
                    best_seek = seek
                    best_algo = algo

        result['optimal'] = {
            'algorithm': best_algo,
            'seek_time': best_seek,
            'all_results': all_results
        }

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
