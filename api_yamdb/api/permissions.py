from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_staff


class IsAuthorOrStaffOrReadOnly(BasePermission):
    '''
    Object-level permission to only allow authors
    of a review/comment (or staff) to edit it.
    '''
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.has_moderator_perm:
            return True

        return obj.author == request.user


class IsRoleAdminOrSuperuser(BasePermission):
    message = 'Такой запрос разрешён только для администраторов.'

    def has_permission(self, request, view):
        return request.user.has_admin_perm


class IsRoleAdminOrSuperuserOrReadOnly(BasePermission):
    message = 'Такой запрос разрешён только для администраторов.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and request.user.has_admin_perm)


class IsRoleModeratorOrSuperuser(BasePermission):
    message = 'Такой запрос разрешён только для модераторов и администраторов.'

    def has_permission(self, request, view):
        return request.user.has_moderator_perm
