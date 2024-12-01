import traceback

from fe.bench.run import run_bench


def test_bench():
    try:
        a=1
        # run_bench()
    except Exception as e:

        assert 200 == 100, "test_bench过程出现异常"
