import 'package:equatable/equatable.dart';
import 'zodiac_sign.dart';

enum FamilyRole {
  parent,
  child,
  sibling,
  grandparent,
  other,
}

class FamilyMember extends Equatable {
  final String id;
  final String name;
  final DateTime birthDate;
  final TimeOfDay? birthTime;
  final String? birthPlace;
  final FamilyRole role;
  final ZodiacSign zodiacSign;
  final String? avatarUrl;
  final DateTime createdAt;

  FamilyMember({
    required this.id,
    required this.name,
    required this.birthDate,
    this.birthTime,
    this.birthPlace,
    required this.role,
    ZodiacSign? zodiacSign,
    this.avatarUrl,
    DateTime? createdAt,
  })  : zodiacSign = zodiacSign ?? ZodiacSign.fromDate(birthDate),
        createdAt = createdAt ?? DateTime.now();

  FamilyMember copyWith({
    String? id,
    String? name,
    DateTime? birthDate,
    TimeOfDay? birthTime,
    String? birthPlace,
    FamilyRole? role,
    ZodiacSign? zodiacSign,
    String? avatarUrl,
    DateTime? createdAt,
  }) {
    return FamilyMember(
      id: id ?? this.id,
      name: name ?? this.name,
      birthDate: birthDate ?? this.birthDate,
      birthTime: birthTime ?? this.birthTime,
      birthPlace: birthPlace ?? this.birthPlace,
      role: role ?? this.role,
      zodiacSign: zodiacSign ?? this.zodiacSign,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  int get age {
    final now = DateTime.now();
    int age = now.year - birthDate.year;
    if (now.month < birthDate.month ||
        (now.month == birthDate.month && now.day < birthDate.day)) {
      age--;
    }
    return age;
  }

  bool get isChild => role == FamilyRole.child;
  bool get isParent => role == FamilyRole.parent;

  String get roleDisplayName {
    switch (role) {
      case FamilyRole.parent:
        return 'Parent';
      case FamilyRole.child:
        return 'Child';
      case FamilyRole.sibling:
        return 'Sibling';
      case FamilyRole.grandparent:
        return 'Grandparent';
      case FamilyRole.other:
        return 'Family Member';
    }
  }

  @override
  List<Object?> get props => [
        id,
        name,
        birthDate,
        birthTime,
        birthPlace,
        role,
        zodiacSign,
        avatarUrl,
        createdAt,
      ];
}

class TimeOfDay extends Equatable {
  final int hour;
  final int minute;

  const TimeOfDay({required this.hour, required this.minute});

  String get formatted {
    final h = hour.toString().padLeft(2, '0');
    final m = minute.toString().padLeft(2, '0');
    return '$h:$m';
  }

  @override
  List<Object?> get props => [hour, minute];
}
