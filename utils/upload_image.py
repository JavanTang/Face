# coding: utf-8
import paramiko

class UploadImage(object):

    def __init__(self, ip, port, username, password):

        '''
        :param ip: web节点ip地址
        :param port: web节点端口
        :param username: web节点登录用户名
        :param password: web节点登录密码
        '''

        self.ip = ip
        self.port = port
        self.username = username
        self.password = password


    def upload_image_to_remote(self, local_image_path, remote_save_path):

        '''
        从算法节点把识别到的人脸图片上传到web节点
        :param local_image_path: 需要上传的算法节点上的图片路径
        :param remote_save_path: 需要上传到web节点的保存路径
        :return:
        '''

        transport = paramiko.Transport(self.ip, self.port)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_image_path, remote_save_path)
        transport.close()