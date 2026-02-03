import '../models/models.dart';

abstract class AstroKinRepository {
  // Family Management
  Future<Family?> getFamily();
  Future<Family> createFamily(String name);
  Future<Family> updateFamily(Family family);
  Future<void> deleteFamily(String familyId);

  // Family Member Management
  Future<FamilyMember> addFamilyMember(FamilyMember member);
  Future<FamilyMember> updateFamilyMember(FamilyMember member);
  Future<void> removeFamilyMember(String memberId);

  // Energy Levels
  Future<FamilyEnergySnapshot> getFamilyEnergy(DateTime date);
  Future<List<FamilyEnergySnapshot>> getEnergyHistory(DateTime start, DateTime end);

  // Astrological Events
  Future<List<AstrologicalEvent>> getUpcomingEvents({int days = 30});
  Future<List<AstrologicalEvent>> getEventsForDate(DateTime date);

  // Parenting Hacks
  Future<List<ParentingHack>> getParentingHacks(FamilyMember child);
  Future<ParentingHack> getDailyHack(FamilyMember child);

  // Sibling Dynamics
  Future<List<SiblingDynamic>> getSiblingDynamics();
  Future<SiblingDynamic> analyzeSiblings(FamilyMember sibling1, FamilyMember sibling2);

  // Retrograde Information
  Future<List<RetrogradeInfo>> getActiveRetrogrades();
  Future<List<RetrogradeInfo>> getUpcomingRetrogrades({int days = 90});
  Future<RetrogradeInfo?> getCurrentMercuryRetrograde();
}
