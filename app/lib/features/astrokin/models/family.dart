import 'package:equatable/equatable.dart';
import 'family_member.dart';
import 'energy_level.dart';

class Family extends Equatable {
  final String id;
  final String name;
  final List<FamilyMember> members;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const Family({
    required this.id,
    required this.name,
    required this.members,
    required this.createdAt,
    this.updatedAt,
  });

  Family copyWith({
    String? id,
    String? name,
    List<FamilyMember>? members,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Family(
      id: id ?? this.id,
      name: name ?? this.name,
      members: members ?? this.members,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  List<FamilyMember> get parents =>
      members.where((m) => m.role == FamilyRole.parent).toList();

  List<FamilyMember> get children =>
      members.where((m) => m.role == FamilyRole.child).toList();

  List<FamilyMember> get siblings =>
      members.where((m) => m.role == FamilyRole.sibling || m.role == FamilyRole.child).toList();

  FamilyMember? getMemberById(String id) {
    try {
      return members.firstWhere((m) => m.id == id);
    } catch (_) {
      return null;
    }
  }

  Family addMember(FamilyMember member) {
    return copyWith(
      members: [...members, member],
      updatedAt: DateTime.now(),
    );
  }

  Family removeMember(String memberId) {
    return copyWith(
      members: members.where((m) => m.id != memberId).toList(),
      updatedAt: DateTime.now(),
    );
  }

  Family updateMember(FamilyMember updatedMember) {
    return copyWith(
      members: members.map((m) => m.id == updatedMember.id ? updatedMember : m).toList(),
      updatedAt: DateTime.now(),
    );
  }

  bool get hasChildren => children.isNotEmpty;
  bool get hasMultipleChildren => children.length > 1;
  int get memberCount => members.length;

  @override
  List<Object?> get props => [id, name, members, createdAt, updatedAt];
}
