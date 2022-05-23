from trains.models import Train


def dfs_paths(graph, start, goal):
    """
    Функция поиска всех возможных маршрутов
    из одого города в другой. Вариант посещения
    одного и того же города более одного раза,
    не рассматривается.
    """
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        if vertex in graph.keys():
            for next_ in graph[vertex] - set(path):
                if next_ == goal:
                    yield path + [next_]
                else:
                    stack.append((next_, path + [next_]))


def get_graph(qs):
    graph = {}
    for q in qs:
        graph.setdefault(q.from_city_id, set())
        graph[q.from_city_id].add(q.to_city_id)
    return graph


def get_routes(request, form) -> dict:
    context = {'form': form}
    qs = Train.objects.all()
    graph = get_graph(qs)
    data = form.cleaned_data
    from_city = data['from_city']
    to_city = data['to_city']
    cities = data['cities']
    travelling_time = data['travelling_time']
    all_routes = len(dfs_paths(graph, from_city.id, to_city.id))
    if not len(list(all_routes)):
        raise ValueError('Маршрута, удовлетворяющего условиям не существует')
    if cities:
        _cities = [city.id for city in cities]
        right_routes = []
        for route in all_routes:
            if all(city in route for city in _cities):
                right_routes.append(route)
        if not right_routes:
            raise ValueError('Маршрута, через эти города невозможен')
    else:
        right_routes = all_routes
    trains = []
    all_trains = {}
    for q in qs:
        all_trains.setdefault((q.from_city_id, q.to_city_id), [])
        all_trains[q.from_city_id, q.to_city_id].append(q)
    for route in right_routes:
        tmp = {}
        tmp['trains'] = []
        total_time = 0
        for i in range(len(route) -  1):
            qs = all_trains[(route[i], route[i+1])]
            q = qs[0]
            total_time += q.travel_time
            tmp['trains'].append(q)
        tmp['total_time'] = total_time
        if total_time <= travelling_time:
            trains.append(tmp)
    if not trains:
        raise ValueError('Время в пути больше заданного')
    return context
