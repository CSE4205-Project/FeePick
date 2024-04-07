def add_namespaces(api):
    from FeePick.controllers.test_controller import ns as test_ns

    api.add_namespace(test_ns)