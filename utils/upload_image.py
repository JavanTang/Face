# coding: utf-8
import os
import paramiko
ip = '47.97.185.63'
port = 9527
username = 'root'
password = 'HZbigdata-cs'
transport = paramiko.Transport((ip, port))
transport.connect(username=username, password=password)
# TODO 这里没有close

def upload_image_to_remote(ip, port, username, password, local_image_path, remote_save_path):

    '''
    从算法节点把识别到的人脸图片上传到web节点
    :param local_image_path: 需要上传的算法节点上的图片路径
    :param remote_save_path: 需要上传到web节点的保存路径
    :return:
    '''
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_image_path, remote_save_path)
    except:
        import traceback
        traceback.print_exc()


def batch_people_upload(paths,camera_id,ids,stamp):
    # remote_save_path = '/raid/home/wangning/1.png'
    remote_save_path = '/docker_data/nginx/web/file/school_storge/man'
    local_path = '/home/tangzhifeng/projects/RealTimeFace/database/old/1701203/1.jpg'
    for index in range(len(ids)):
        remote_path = os.path.join(remote_save_path, ids[index], str(camera_id), stamp+'.jpg')
        upload_image_to_remote(ip,port,username,password,paths[index],remote_save_path)

