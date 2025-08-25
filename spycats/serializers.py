from rest_framework import serializers
from .models import Breed, SpyCat, Mission, Target, CompleteChoices

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = '__all__'

class SpyCatSerializer(serializers.ModelSerializer):
    breed = serializers.CharField(source='breed.name')
    class Meta:
        model = SpyCat
        fields = ['id', 'name', 'experience', 'breed', 'salary']

    def create(self, validated_data):
        breed_name = validated_data.pop('breed')['name']
        try:
            breed = Breed.objects.get(name=breed_name)
        except Breed.DoesNotExist:
            raise serializers.ValidationError({'breed': f'Breed with name "{breed_name}" does not exist.'})
        spycat = SpyCat.objects.create(breed=breed, **validated_data)
        return spycat

    def update(self, instance, validated_data):
        breed_data = validated_data.pop('breed', None)
        if breed_data:
            breed_name = breed_data['name']
            try:
                breed = Breed.objects.get(name=breed_name)
            except Breed.DoesNotExist:
                raise serializers.ValidationError({'breed': f'Breed with name "{breed_name}" does not exist.'})
            instance.breed = breed
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = '__all__'

    def validate(self, attrs):
        spy_cat = attrs.get('spy_cat')
        if self.instance:
            return attrs
        if Mission.objects.filter(spy_cat=spy_cat).exclude(complete_state=CompleteChoices.COMPLETED).exists():
            raise serializers.ValidationError('This cat already has an active mission.')
        return attrs

    def create(self, validated_data):
        mission = super().create(validated_data)
        return mission

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'

    def validate(self, attrs):
        mission = attrs.get('mission') or self.instance.mission if self.instance else None
        if mission:
            target_count = mission.targets.count()
            if not self.instance and target_count >= 3:
                raise serializers.ValidationError('A mission can have a maximum of 3 targets.')
        return attrs

    def update(self, instance, validated_data):
        if instance.complete_state == CompleteChoices.COMPLETED:
            if 'notes' in validated_data:
                raise serializers.ValidationError('Notes cannot be updated for a completed target.')

        complete_state = validated_data.get('complete_state')
        if complete_state == CompleteChoices.COMPLETED and instance.complete_state != CompleteChoices.COMPLETED:
            instance.complete_state = CompleteChoices.COMPLETED
            instance.save()
            mission = instance.mission
            if all(t.complete_state == CompleteChoices.COMPLETED for t in mission.targets.all()):
                mission.complete_state = CompleteChoices.COMPLETED
                mission.save()

        return super().update(instance, validated_data)

    def create(self, validated_data):
        mission = validated_data.get('mission')
        if mission.targets.count() >= 3:
            raise serializers.ValidationError('A mission can have a maximum of 3 targets.')
        target = super().create(validated_data)

        if mission.targets.count() < 1:
            raise serializers.ValidationError('A mission must have at least 1 target.')
        return target
