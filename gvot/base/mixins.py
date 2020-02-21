class UniqPage:
    @classmethod
    def can_create_at(cls, parent):
        # Seulement une instance possible
        return not cls.objects.exists() and super().can_create_at(parent)
