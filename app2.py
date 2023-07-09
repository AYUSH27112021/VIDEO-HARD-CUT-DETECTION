from flask import Flask, render_template, request, send_file,Response,redirect,url_for,jsonify,send_from_directory
import matplotlib,time,os,cv2,numpy as np
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

video_file_path = os.path.join('static', 'uploads', 'video.mp4')
fps_file_path = os.path.join('static', 'uploads', 'fps.txt')
histogram_image_path = os.path.join('static', 'uploads', 'histogram.svg')
histogram_diff_path = os.path.join('static', 'uploads', 'histogram_diff.txt')
threshold_file_path = os.path.join('static', 'uploads', 'adaptive_threshold.txt')
cuts_file_path = os.path.join('static', 'uploads', 'cuts.txt')

fps_value = None
allowed_extensions = {'mp4', 'avi', 'mkv'}

@app.route('/', methods=['GET', 'POST'])

def index():
    uploads_folder = os.path.join(app.static_folder, 'uploads')
    for filename in os.listdir(uploads_folder):
        file_path = os.path.join(uploads_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    if request.method == 'POST':
        if 'video' not in request.files:
            return render_template('error2.html', message='No video file selected')

        video_file = request.files['video']
        if video_file.filename == '':
            return render_template('error2.html', message='No video file selected')

        if video_file and is_allowed_extension(video_file.filename):
            video_file.save(video_file_path)
            return redirect(url_for('upload_success'))
        else:
            return render_template('error2.html', message='Invalid file format')

    return render_template('upload.html')

@app.route('/upload_success')
def upload_success():
    return render_template('index.html', message='Video was uploaded successfully')

@app.route('/play')
def play():
    if not os.path.exists(video_file_path):
        return render_template('error.html', message='No video uploaded')
    return send_file(video_file_path, mimetype='video/mp4')

def is_allowed_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/fps', methods=['POST', 'GET'])
def fps():
    return render_template('fps.html')

@app.route('/calculate_fps', methods=['POST'])
def calculate_fps():
    if os.path.exists(video_file_path):
        cap = cv2.VideoCapture(video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        with open(fps_file_path, 'w') as f:
            f.write(str(fps))
        return jsonify(fps=fps)
    else:
        return render_template('error.html', message='No video file selected')

@app.route('/histogram')
def histogram():
    return render_template('histogram.html')

def calculate_histogram(video_file_path, histogram_image_path):
    cap = cv2.VideoCapture(video_file_path)

    if not cap.isOpened():
        return 'error', 'Error opening video file'

    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return 'error', 'Error reading first frame'


    prev_hsv = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2HSV)


    hist_diffs = []


    frame_num = 1
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


        hist_prev, _ = np.histogramdd(prev_hsv.reshape(-1, 3), bins=(8, 4, 4), range=((0, 180), (0, 256), (0, 256)))
        hist_curr, _ = np.histogramdd(hsv.reshape(-1, 3), bins=(8, 4, 4), range=((0, 180), (0, 256), (0, 256)))


        hist_diff = np.sum(np.abs(hist_prev - hist_curr))
        hist_diffs.append(hist_diff)


        prev_hsv = hsv


        frame_num += 1
    arr = np.array(hist_diffs)
    np.savetxt(histogram_diff_path, arr)

    plt.figure(figsize=(16,8))
    plt.plot(hist_diffs)
    plt.title('Histogram Differences')
    plt.xlabel('Frame number')
    plt.ylabel('Histogram difference')


    plt.savefig(histogram_image_path,dpi=600)
    plt.close()

    cap.release()

    return 'success', histogram_image_path

@app.route('/render_histogram', methods=['POST'])
def render_histogram():
    status, result = calculate_histogram(video_file_path, histogram_image_path)
    if status == 'success':
        return jsonify({'status': 'success', 'histogram_image': result})
    else:
        return jsonify({'status': 'error'})

@app.route('/threshold', methods=['POST', 'GET'])
def threshold():
    return render_template('threshold.html')

@app.route('/calculate_threshold', methods=['POST'])
def calculate_threshold():
    if os.path.exists(histogram_diff_path):
        print('true')
        pixel_diff_values = np.loadtxt(histogram_diff_path)
        mean_value = np.mean(pixel_diff_values)
        std_value = np.std(pixel_diff_values)
        threshold = mean_value + 3 * std_value    
        with open(threshold_file_path, 'w') as f:
            f.write(str(threshold))
        return jsonify(threshold=threshold)
    else:
        return render_template('error.html', message='Error in histogram calculation')

@app.route('/cuts', methods=['POST', 'GET'])
def cuts():
    return render_template('cuts.html')

@app.route('/calculate_cuts', methods=['POST'])
def calculate_cuts():
    if os.path.exists(video_file_path):
        cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        return render_template('error.html', message='Error opening video file')

    ret, prev_frame = cap.read()
    if not ret:
        return render_template('error.html', message='Error reading first frame')
    cap.release()
    count=0
    pixel_diff_values = np.loadtxt(histogram_diff_path)
    with open(threshold_file_path) as f:
        adaptive_threshold=f.read()
        f.close()
    with open(fps_file_path) as f:
        fps=f.read()
        f.close()
    for frame_number in range(pixel_diff_values.shape[0]):
        if pixel_diff_values[frame_number] > float(adaptive_threshold):
            count+=1
            time_sec = ((frame_number+1 )/ float(fps))
            seconds_to_hhmmss = lambda seconds: f'{int(seconds // 3600):02d}:{int((seconds % 3600) // 60):02d}:{seconds % 60:06.3f}'
            formatted_time = seconds_to_hhmmss(time_sec)
            with open(cuts_file_path, 'a') as f:
                f.write(f"Cut detected at frame {frame_number} at time ({formatted_time})\n")  
    with open(cuts_file_path, 'a') as f:
                f.write(f"total Cuts detected {count}")
    return jsonify(total_cuts=count)
@app.route('/static/cuts.txt')
def serve_cuts_file():
    return send_from_directory('static\\uploads', 'cuts.txt')
@app.route('/download_cuts')
def download_cuts():
    return send_file('static\\uploads\\cuts.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

