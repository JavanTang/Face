# coding: utf-8
import paramiko

def upload_image_to_remote(ip, port, username, password, local_image_path, remote_save_path):

    '''
    从算法节点把识别到的人脸图片上传到web节点
    :param local_image_path: 需要上传的算法节点上的图片路径
    :param remote_save_path: 需要上传到web节点的保存路径
    :return:
    '''

    transport = paramiko.Transport(ip, port)
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_image_path, remote_save_path)
    transport.close()