class ResourceAction:
    @property
    def read(self):
        return 'view'

    @property
    def write(self):
        return 'edit'

    @property
    def delete(self):
        return 'delete'


resource_action = ResourceAction()
