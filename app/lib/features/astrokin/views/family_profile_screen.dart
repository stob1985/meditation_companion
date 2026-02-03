import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../theme/astrokin_theme.dart';

class FamilyProfileScreen extends StatelessWidget {
  const FamilyProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        if (!state.hasFamily) {
          return _buildCreateFamilyView(context);
        }

        return Scaffold(
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(AstroKinSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Family Header
                _buildFamilyHeader(context, state.family!),

                const SizedBox(height: AstroKinSpacing.lg),

                // Family Members
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Family Members',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    TextButton.icon(
                      onPressed: () => _showAddMemberDialog(context),
                      icon: const Icon(Icons.add, size: 18),
                      label: const Text('Add'),
                    ),
                  ],
                ),
                const SizedBox(height: AstroKinSpacing.sm),

                if (state.family!.members.isEmpty)
                  _buildEmptyMembersCard(context)
                else
                  ...state.family!.members.map((member) => Padding(
                        padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                        child: FamilyMemberCard(
                          member: member,
                          onTap: () => _showMemberDetails(context, member),
                          onEdit: () => _showEditMemberDialog(context, member),
                          onDelete: () => _showDeleteConfirmation(context, member),
                        ),
                      )),

                const SizedBox(height: AstroKinSpacing.lg),

                // Family Statistics
                if (state.family!.members.isNotEmpty) _buildFamilyStats(context, state.family!),
              ],
            ),
          ),
          floatingActionButton: FloatingActionButton.extended(
            onPressed: () => _showAddMemberDialog(context),
            icon: const Icon(Icons.person_add),
            label: const Text('Add Member'),
          ),
        );
      },
    );
  }

  Widget _buildCreateFamilyView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(AstroKinSpacing.xl),
              decoration: BoxDecoration(
                gradient: AstroKinTheme.primaryGradient,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.family_restroom,
                size: 80,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: AstroKinSpacing.xl),
            Text(
              'Create Your Family',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Text(
              'Start your AstroKin journey by creating a family profile. Add family members to get personalized insights.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.xl),
            ElevatedButton.icon(
              onPressed: () => _showCreateFamilyDialog(context),
              icon: const Icon(Icons.add),
              label: const Text('Create Family'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: AstroKinSpacing.xl,
                  vertical: AstroKinSpacing.md,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFamilyHeader(BuildContext context, Family family) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(AstroKinSpacing.md),
              decoration: BoxDecoration(
                gradient: AstroKinTheme.primaryGradient,
                borderRadius: BorderRadius.circular(AstroKinRadius.md),
              ),
              child: const Icon(
                Icons.family_restroom,
                color: Colors.white,
                size: 32,
              ),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    family.name,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  Text(
                    '${family.memberCount} members',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AstroKinTheme.textSecondary,
                        ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.edit_outlined),
              onPressed: () => _showEditFamilyDialog(context, family),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyMembersCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          children: [
            Icon(
              Icons.person_add_outlined,
              size: 48,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Text(
              'No family members yet',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Text(
              'Add family members to start getting personalized astrological insights',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFamilyStats(BuildContext context, Family family) {
    final elementCounts = <Element, int>{};
    for (final member in family.members) {
      final element = member.zodiacSign.element;
      elementCounts[element] = (elementCounts[element] ?? 0) + 1;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Family Elements',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: Element.values.map((element) {
                final count = elementCounts[element] ?? 0;
                return Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(AstroKinSpacing.md),
                      decoration: BoxDecoration(
                        color: AstroKinTheme.getZodiacColor(element.name).withValues(alpha: 0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        _getElementEmoji(element),
                        style: const TextStyle(fontSize: 24),
                      ),
                    ),
                    const SizedBox(height: AstroKinSpacing.xs),
                    Text(
                      element.name[0].toUpperCase() + element.name.substring(1),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    Text(
                      '$count',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: AstroKinTheme.getZodiacColor(element.name),
                          ),
                    ),
                  ],
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  String _getElementEmoji(Element element) {
    switch (element) {
      case Element.fire:
        return '🔥';
      case Element.earth:
        return '🌍';
      case Element.air:
        return '💨';
      case Element.water:
        return '💧';
    }
  }

  void _showCreateFamilyDialog(BuildContext context) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create Family'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Family Name',
            hintText: 'e.g., The Smith Family',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (controller.text.trim().isNotEmpty) {
                context.read<AstroKinBloc>().add(CreateFamily(controller.text.trim()));
                Navigator.pop(ctx);
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showEditFamilyDialog(BuildContext context, Family family) {
    final controller = TextEditingController(text: family.name);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Family Name'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Family Name',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (controller.text.trim().isNotEmpty) {
                final updated = family.copyWith(name: controller.text.trim());
                context.read<AstroKinBloc>().add(AddFamilyMember(updated.members.first));
                Navigator.pop(ctx);
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showAddMemberDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _AddMemberSheet(
        onSave: (member) {
          context.read<AstroKinBloc>().add(AddFamilyMember(member));
        },
      ),
    );
  }

  void _showEditMemberDialog(BuildContext context, FamilyMember member) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _AddMemberSheet(
        member: member,
        onSave: (updated) {
          context.read<AstroKinBloc>().add(UpdateFamilyMember(updated));
        },
      ),
    );
  }

  void _showMemberDetails(BuildContext context, FamilyMember member) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _MemberDetailsSheet(member: member),
    );
  }

  void _showDeleteConfirmation(BuildContext context, FamilyMember member) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Remove Member'),
        content: Text('Are you sure you want to remove ${member.name} from the family?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<AstroKinBloc>().add(RemoveFamilyMember(member.id));
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Remove'),
          ),
        ],
      ),
    );
  }
}

class _AddMemberSheet extends StatefulWidget {
  final FamilyMember? member;
  final Function(FamilyMember) onSave;

  const _AddMemberSheet({this.member, required this.onSave});

  @override
  State<_AddMemberSheet> createState() => _AddMemberSheetState();
}

class _AddMemberSheetState extends State<_AddMemberSheet> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late DateTime _birthDate;
  late FamilyRole _role;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.member?.name ?? '');
    _birthDate = widget.member?.birthDate ?? DateTime(2010, 1, 1);
    _role = widget.member?.role ?? FamilyRole.child;
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(AstroKinRadius.xl)),
      ),
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: AstroKinSpacing.sm),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Header
            Padding(
              padding: const EdgeInsets.all(AstroKinSpacing.md),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                  Text(
                    widget.member == null ? 'Add Member' : 'Edit Member',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  TextButton(
                    onPressed: _saveMember,
                    child: const Text('Save'),
                  ),
                ],
              ),
            ),

            const Divider(height: 1),

            // Form
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AstroKinSpacing.lg),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                        labelText: 'Name',
                        hintText: 'Enter name',
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter a name';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: AstroKinSpacing.lg),

                    // Role
                    Text(
                      'Role',
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: AstroKinSpacing.sm),
                    Wrap(
                      spacing: AstroKinSpacing.sm,
                      children: FamilyRole.values.map((role) {
                        return ChoiceChip(
                          label: Text(_getRoleLabel(role)),
                          selected: _role == role,
                          onSelected: (selected) {
                            if (selected) {
                              setState(() => _role = role);
                            }
                          },
                        );
                      }).toList(),
                    ),

                    const SizedBox(height: AstroKinSpacing.lg),

                    // Birth Date
                    Text(
                      'Birth Date',
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: AstroKinSpacing.sm),
                    InkWell(
                      onTap: _selectBirthDate,
                      child: Container(
                        padding: const EdgeInsets.all(AstroKinSpacing.md),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(AstroKinRadius.md),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '${_birthDate.month}/${_birthDate.day}/${_birthDate.year}',
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                            const Icon(Icons.calendar_today),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: AstroKinSpacing.lg),

                    // Zodiac Preview
                    _buildZodiacPreview(context),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildZodiacPreview(BuildContext context) {
    final sign = ZodiacSign.fromDate(_birthDate);
    return Card(
      color: AstroKinTheme.getZodiacColor(sign.element.name).withValues(alpha: 0.1),
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Row(
          children: [
            Text(
              sign.symbol,
              style: const TextStyle(fontSize: 40),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  sign.name,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                Text(
                  '${sign.element.name[0].toUpperCase()}${sign.element.name.substring(1)} Sign ${sign.elementEmoji}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Text(
                  'Ruled by ${sign.rulingPlanet}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AstroKinTheme.textSecondary,
                      ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getRoleLabel(FamilyRole role) {
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
        return 'Other';
    }
  }

  void _selectBirthDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _birthDate,
      firstDate: DateTime(1920),
      lastDate: DateTime.now(),
    );
    if (date != null) {
      setState(() => _birthDate = date);
    }
  }

  void _saveMember() {
    if (_formKey.currentState!.validate()) {
      final member = FamilyMember(
        id: widget.member?.id ?? 'member_${DateTime.now().millisecondsSinceEpoch}',
        name: _nameController.text.trim(),
        birthDate: _birthDate,
        role: _role,
      );
      widget.onSave(member);
      Navigator.pop(context);
    }
  }
}

class _MemberDetailsSheet extends StatelessWidget {
  final FamilyMember member;

  const _MemberDetailsSheet({required this.member});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AstroKinSpacing.lg),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(AstroKinRadius.xl)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.only(bottom: AstroKinSpacing.md),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Avatar
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AstroKinTheme.getZodiacColor(member.zodiacSign.element.name),
                  AstroKinTheme.getZodiacColor(member.zodiacSign.element.name).withValues(alpha: 0.5),
                ],
              ),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                member.zodiacSign.symbol,
                style: const TextStyle(fontSize: 40, color: Colors.white),
              ),
            ),
          ),

          const SizedBox(height: AstroKinSpacing.md),

          Text(
            member.name,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          Text(
            '${member.roleDisplayName} - ${member.age} years old',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AstroKinTheme.textSecondary,
                ),
          ),

          const SizedBox(height: AstroKinSpacing.lg),

          // Zodiac Info
          Card(
            child: Padding(
              padding: const EdgeInsets.all(AstroKinSpacing.md),
              child: Column(
                children: [
                  _buildInfoRow(context, 'Sun Sign', '${member.zodiacSign.name} ${member.zodiacSign.symbol}'),
                  const Divider(),
                  _buildInfoRow(context, 'Element', '${member.zodiacSign.element.name[0].toUpperCase()}${member.zodiacSign.element.name.substring(1)} ${member.zodiacSign.elementEmoji}'),
                  const Divider(),
                  _buildInfoRow(context, 'Ruling Planet', member.zodiacSign.rulingPlanet),
                  const Divider(),
                  _buildInfoRow(context, 'Birth Date', '${member.birthDate.month}/${member.birthDate.day}/${member.birthDate.year}'),
                ],
              ),
            ),
          ),

          const SizedBox(height: AstroKinSpacing.md),
        ],
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AstroKinSpacing.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AstroKinTheme.textSecondary,
                ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }
}
