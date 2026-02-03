import 'package:equatable/equatable.dart';
import '../models/models.dart';

abstract class AstroKinEvent extends Equatable {
  const AstroKinEvent();

  @override
  List<Object?> get props => [];
}

// Family Events
class LoadFamily extends AstroKinEvent {}

class CreateFamily extends AstroKinEvent {
  final String name;

  const CreateFamily(this.name);

  @override
  List<Object?> get props => [name];
}

class AddFamilyMember extends AstroKinEvent {
  final FamilyMember member;

  const AddFamilyMember(this.member);

  @override
  List<Object?> get props => [member];
}

class UpdateFamilyMember extends AstroKinEvent {
  final FamilyMember member;

  const UpdateFamilyMember(this.member);

  @override
  List<Object?> get props => [member];
}

class RemoveFamilyMember extends AstroKinEvent {
  final String memberId;

  const RemoveFamilyMember(this.memberId);

  @override
  List<Object?> get props => [memberId];
}

// Energy Events
class LoadFamilyEnergy extends AstroKinEvent {
  final DateTime? date;

  const LoadFamilyEnergy({this.date});

  @override
  List<Object?> get props => [date];
}

class LoadEnergyHistory extends AstroKinEvent {
  final DateTime startDate;
  final DateTime endDate;

  const LoadEnergyHistory({required this.startDate, required this.endDate});

  @override
  List<Object?> get props => [startDate, endDate];
}

// Astrological Events
class LoadUpcomingEvents extends AstroKinEvent {
  final int days;

  const LoadUpcomingEvents({this.days = 30});

  @override
  List<Object?> get props => [days];
}

class LoadEventsForDate extends AstroKinEvent {
  final DateTime date;

  const LoadEventsForDate(this.date);

  @override
  List<Object?> get props => [date];
}

// Parenting Hacks Events
class LoadParentingHacks extends AstroKinEvent {
  final FamilyMember child;

  const LoadParentingHacks(this.child);

  @override
  List<Object?> get props => [child];
}

class LoadDailyHack extends AstroKinEvent {
  final FamilyMember child;

  const LoadDailyHack(this.child);

  @override
  List<Object?> get props => [child];
}

// Sibling Dynamics Events
class LoadSiblingDynamics extends AstroKinEvent {}

class AnalyzeSiblings extends AstroKinEvent {
  final FamilyMember sibling1;
  final FamilyMember sibling2;

  const AnalyzeSiblings({required this.sibling1, required this.sibling2});

  @override
  List<Object?> get props => [sibling1, sibling2];
}

// Retrograde Events
class LoadActiveRetrogrades extends AstroKinEvent {}

class LoadUpcomingRetrogrades extends AstroKinEvent {
  final int days;

  const LoadUpcomingRetrogrades({this.days = 90});

  @override
  List<Object?> get props => [days];
}

// Dashboard Events
class LoadDashboard extends AstroKinEvent {}

class RefreshDashboard extends AstroKinEvent {}

// Navigation Events
class SelectChild extends AstroKinEvent {
  final FamilyMember child;

  const SelectChild(this.child);

  @override
  List<Object?> get props => [child];
}

class SelectDate extends AstroKinEvent {
  final DateTime date;

  const SelectDate(this.date);

  @override
  List<Object?> get props => [date];
}
