import time
import wave
import pyaudio
import numpy as np

def alarming(wav_path):

    """
    播放报警音频
    :param wav_path: 音频文件所在路径
    """

    chunk = 1024
    f = wave.open(wav_path,"rb")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    data = f.readframes(chunk)

    while data != b'':
        stream.write(data)
        data = f.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()

def cos_sim(vector_a, vector_b):

    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """

    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim

def stay_detect(cameraImg, before_last_time, all_people, cameraKey, sftp_obj, image_save_path):

    """
    异常逗留检测
    :param cameraImg: 摄像头读取的当前帧的图片
    :param before_last_time: 上一帧图片检测到的人脸信息
    :param all_people: 当前帧图片检测到的人脸信息
    :param cameraKey:  摄像头编号
    :param sftp_obj: 远程传输文件的对象
    :param image_save_path: 远程web节点的异常场景图片保存路径
    :return:
    """

    if before_last_time == []:
        return all_people
    else:
        embs = list()
        first_appear_time = list()
        final_disappear_time = list()
        box = list()
        for people in before_last_time:
            embs.append(people[0])
            first_appear_time.append(people[1])
            final_disappear_time.append(people[2])
            box.append(people[3])

        new_embs = list()
        new_first_appear_time = list()
        new_final_disappear_time = list()
        new_box = list()
        for people in all_people:
            new_embs.append(people[0])
            new_first_appear_time.append(people[1])
            new_final_disappear_time.append(people[2])
            new_box.append(people[3])

        all_people_info = list()
        threshold = 0.9
        for i in range(len(new_embs)):
            max = 0
            max_index = 1000
            people_info = list()
            for j in range(len(embs)):
                dist = cos_sim(new_embs[i], embs[j])
                if dist > max:
                    max = dist
                    max_index = j
            if max >= threshold:
                final_disappear_time = time.time()
                if new_first_appear_time[i] - first_appear_time[max_index] > 2:
                    print('逗留报警')
                    alarming()

                    # 联合调试的时候可能需要再改一下
                    '''
                    cv2.imwrite('stay_abnormal.jpg', cameraImg)

                    # stay_abnormal.jpg上传到web节点指定目录下
                    sftp_obj.upload_image_to_remote('stay_abnormal.jpg', os.path.join(image_save_path, str(int((time.time())) + '.jpg')))

                    '''

                    people_info.append(new_embs[i])
                    people_info.append(time.time())
                    people_info.append(final_disappear_time)
                    people_info.append(new_box[i])
                else:
                    people_info.append(new_embs[i])
                    people_info.append(first_appear_time[max_index])
                    people_info.append(final_disappear_time)
                    people_info.append(new_box[i])

            else:
                people_info.append(new_embs[i])
                people_info.append(new_first_appear_time[i])
                final_disappear_time = time.time()
                people_info.append(final_disappear_time)
                people_info.append(new_box[i])

            all_people_info.append(people_info)

        return all_people_info







