def upload_location(instance, filename):
    model = instance.__class__
    last_obj = model.objects.order_by("id").last()

    if last_obj:
        new_id = last_obj.id + 1
    else:
        new_id = 1

    return "comment/%s/%s" % (new_id, filename)
