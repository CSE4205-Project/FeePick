def add_namespaces(api):
    from FeePick.api.test_controller import ns as test_ns

    api.add_namespace(test_ns)