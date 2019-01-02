import traceback


def UnitTestDecorator(obj):
    """单元测试装饰器，在单元测试的时候可以开启单元测试模式，不影响程序正常运行时的状态
    """

    def set_test_option_on(self):
        self.test_option = True

    def get_test_option(self):
        return self.test_option

    obj.test_option = False
    obj.set_test_option_on = set_test_option_on
    obj.get_test_option = get_test_option
    return obj

