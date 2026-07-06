

# ============================================================================
# INLINE ADMINS
# ============================================================================


# class MenuItemInline(admin.TabularInline):
#     model = MenuItemEntity
#     extra = 0
#     fields = ("code", "label", "url_name", "url_path", "sort_order", "is_active", "is_hidden")
#     readonly_fields = ("uuid", "created_at")
#     show_change_link = True
#     ordering = ("sort_order",)


# class MenuItemRoleInline(admin.TabularInline):
#     model = MenuItemRoleEntity
#     extra = 0
#     fields = ("role",)
#     autocomplete_fields = ("role",)


# # ============================================================================
# # MENU GROUP ADMIN
# # ============================================================================


# @admin.register(MenuGroupEntity)
# class MenuGroupAdmin(admin.ModelAdmin):
#     list_display = (
#         "label",
#         "code",
#         "tenant",
#         "sort_order",
#         "is_active",
#         "item_count",
#         "created_at",
#     )
#     list_filter = ("is_active", "tenant")
#     search_fields = ("code", "label", "tenant__name", "tenant__code")
#     readonly_fields = ("uuid", "created_at", "updated_at")
#     ordering = ("tenant", "sort_order")
#     raw_id_fields = ("tenant",)
#     inlines = [MenuItemInline]

#     fieldsets = (
#         (
#             "Identification",
#             {
#                 "fields": ("tenant", "code", "uuid", "label"),
#             },
#         ),
#         (
#             "Display",
#             {
#                 "fields": ("icon", "sort_order"),
#             },
#         ),
#         (
#             "Status",
#             {
#                 "fields": ("is_active",),
#             },
#         ),
#         (
#             "Timestamps",
#             {
#                 "fields": ("created_at", "updated_at"),
#                 "classes": ("collapse",),
#             },
#         ),
#     )

#     @admin.display(description="Items")
#     def item_count(self, obj):
#         count = obj.menu_items.count()
#         return format_html('<span style="font-weight:bold">{}</span>', count)


# # ============================================================================
# # MENU ITEM ADMIN
# # ============================================================================


# @admin.register(MenuItemEntity)
# class MenuItemAdmin(admin.ModelAdmin):
#     list_display = (
#         "label",
#         "code",
#         "tenant",
#         "group",
#         "parent",
#         "depth_display",
#         "sort_order",
#         "is_active",
#         "is_hidden",
#         "created_at",
#     )
#     list_filter = ("is_active", "is_hidden", "tenant", "group")
#     search_fields = ("code", "label", "url_name", "url_path", "permission_code")
#     readonly_fields = ("uuid", "created_at", "updated_at")
#     ordering = ("tenant", "group", "sort_order")
#     raw_id_fields = ("tenant", "group", "parent")
#     inlines = [MenuItemRoleInline]

#     fieldsets = (
#         (
#             "Identification",
#             {
#                 "fields": ("tenant", "uuid", "code", "label"),
#             },
#         ),
#         (
#             "Hierarchy",
#             {
#                 "fields": ("group", "parent"),
#             },
#         ),
#         (
#             "URL Routing",
#             {
#                 "fields": ("url_name", "url_path"),
#             },
#         ),
#         (
#             "Display",
#             {
#                 "fields": ("icon", "sort_order", "open_in_new_tab"),
#             },
#         ),
#         (
#             "Badge",
#             {
#                 "fields": ("badge_text", "badge_color"),
#                 "classes": ("collapse",),
#             },
#         ),
#         (
#             "Permissions",
#             {
#                 "fields": ("permission_code",),
#             },
#         ),
#         (
#             "Status",
#             {
#                 "fields": ("is_active", "is_hidden"),
#             },
#         ),
#         (
#             "Timestamps",
#             {
#                 "fields": ("created_at", "updated_at"),
#                 "classes": ("collapse",),
#             },
#         ),
#     )

#     @admin.display(description="Depth")
#     def depth_display(self, obj):
#         depth = obj.get_depth()
#         prefix = "—" * depth
#         return f"{prefix} {depth}" if depth else "0 (root)"


# # ============================================================================
# # AUDIT LOG ADMINS
# # ============================================================================


# @admin.register(MenuAuditLogEntity)
# class MenuAuditLogAdmin(admin.ModelAdmin):
#     list_display = ("action", "tenant", "actor", "created_at")
#     list_filter = ("action", "tenant")
#     search_fields = ("actor__username", "tenant__code")
#     readonly_fields = ("tenant", "action", "actor", "old_values", "new_values", "created_at")
#     ordering = ("-created_at",)

#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False


# @admin.register(MenuItemRoleAuditLogEntity)
# class MenuItemRoleAuditLogAdmin(admin.ModelAdmin):
#     list_display = (
#         "action",
#         "tenant",
#         "menu_item",
#         "role",
#         "actor",
#         "affected_count",
#         "created_at",
#     )
#     list_filter = ("action", "tenant")
#     search_fields = ("actor__username", "actor_username", "tenant__code", "menu_item__code")
#     readonly_fields = (
#         "tenant", "menu_item", "role", "action", "actor", "actor_username",
#         "affected_count", "reason", "created_at",
#     )
#     ordering = ("-created_at",)

#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False
