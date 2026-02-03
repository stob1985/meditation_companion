import 'package:flutter/material.dart';
import '../models/models.dart';
import '../theme/astrokin_theme.dart';

class FamilyMemberCard extends StatelessWidget {
  final FamilyMember member;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const FamilyMemberCard({
    super.key,
    required this.member,
    this.onTap,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        child: Padding(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Row(
            children: [
              _buildAvatar(context),
              const SizedBox(width: AstroKinSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      member.name,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Text(
                          member.zodiacSign.symbol,
                          style: const TextStyle(fontSize: 16),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          member.zodiacSign.name,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AstroKinTheme.textSecondary,
                              ),
                        ),
                        const SizedBox(width: AstroKinSpacing.sm),
                        Text(
                          member.zodiacSign.elementEmoji,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${member.roleDisplayName} - ${member.age} years old',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AstroKinTheme.textSecondary,
                          ),
                    ),
                  ],
                ),
              ),
              if (onEdit != null || onDelete != null)
                PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'edit') onEdit?.call();
                    if (value == 'delete') onDelete?.call();
                  },
                  itemBuilder: (context) => [
                    if (onEdit != null)
                      const PopupMenuItem(
                        value: 'edit',
                        child: Row(
                          children: [
                            Icon(Icons.edit_outlined, size: 20),
                            SizedBox(width: 8),
                            Text('Edit'),
                          ],
                        ),
                      ),
                    if (onDelete != null)
                      const PopupMenuItem(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete_outlined, size: 20, color: Colors.red),
                            SizedBox(width: 8),
                            Text('Delete', style: TextStyle(color: Colors.red)),
                          ],
                        ),
                      ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar(BuildContext context) {
    final elementColor = AstroKinTheme.getZodiacColor(member.zodiacSign.element.name);

    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            elementColor.withValues(alpha: 0.8),
            elementColor.withValues(alpha: 0.5),
          ],
        ),
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          member.zodiacSign.symbol,
          style: const TextStyle(
            fontSize: 28,
            color: Colors.white,
          ),
        ),
      ),
    );
  }
}

class CompactMemberChip extends StatelessWidget {
  final FamilyMember member;
  final bool isSelected;
  final VoidCallback? onTap;

  const CompactMemberChip({
    super.key,
    required this.member,
    this.isSelected = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final elementColor = AstroKinTheme.getZodiacColor(member.zodiacSign.element.name);

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(
          horizontal: AstroKinSpacing.md,
          vertical: AstroKinSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: isSelected ? elementColor.withValues(alpha: 0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(AstroKinRadius.xl),
          border: Border.all(
            color: isSelected ? elementColor : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              member.zodiacSign.symbol,
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(width: 6),
            Text(
              member.name,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
