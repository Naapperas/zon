import pod

validator = pod.record({
    "a": pod.number(),
    "b": pod.optional(pod.string()),
    "c": pod.element_list(pod.integer()),

})

validator.validate({
    "a": 1,
    "b": "hello",
    "c": [1, 2, 3, 4, 5]
})
print(validator.errors)
validator.validate({
    "a": 1,
    "c": [1, 2, 3, 4, 5]
})

print(validator.errors)