import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

const createPetSchema = z.object({
  name: z.string().min(1, 'Name is required.').max(80, 'Name must be 80 characters or less.'),
  species: z.string().min(1, 'Species is required.').max(50, 'Species must be 50 characters or less.'),
  bio: z.string().max(1000, 'Bio must be 1000 characters or less.').optional(),
});

export function CreatePetForm() {
  const navigate = useNavigate();
  const [formValues, setFormValues] = useState({
    name: '',
    species: '',
    bio: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((previous) => ({ ...previous, [name]: value }));
    setErrors((previous) => ({ ...previous, [name]: '' }));
    setSubmitMessage('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const parsed = createPetSchema.safeParse({
      ...formValues,
      bio: formValues.bio.trim() || undefined,
    });

    if (!parsed.success) {
      const fieldErrors = parsed.error.flatten().fieldErrors;
      setErrors({
        name: fieldErrors.name?.[0] ?? '',
        species: fieldErrors.species?.[0] ?? '',
        bio: fieldErrors.bio?.[0] ?? '',
      });
      return;
    }

    setErrors({});
    setSubmitMessage('');
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/pets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
        },
        body: JSON.stringify({
          name: parsed.data.name.trim(),
          species: parsed.data.species.trim(),
          bio: parsed.data.bio,
        }),
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(payload?.detail || `Request failed with status ${response.status}`);
      }

      localStorage.setItem('active_pet_id', String(payload.id));
      navigate('/');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error.';
      setSubmitMessage(`Could not create pet. ${message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="grid gap-3" onSubmit={handleSubmit} noValidate>
      <div className="grid gap-1 text-left">
        <Label htmlFor="pet-name">Pet name</Label>
        <Input
          id="pet-name"
          name="name"
          placeholder="Milo"
          value={formValues.name}
          onChange={handleChange}
          aria-invalid={Boolean(errors.name)}
        />
        {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
      </div>

      <div className="grid gap-1 text-left">
        <Label htmlFor="pet-species">Species</Label>
        <Input
          id="pet-species"
          name="species"
          placeholder="Dog"
          value={formValues.species}
          onChange={handleChange}
          aria-invalid={Boolean(errors.species)}
        />
        {errors.species && <p className="text-sm text-destructive">{errors.species}</p>}
      </div>

      <div className="grid gap-1 text-left">
        <Label htmlFor="pet-bio">Bio (optional)</Label>
        <textarea
          id="pet-bio"
          name="bio"
          className="min-h-24 rounded-md border bg-background px-3 py-2 text-sm"
          placeholder="Friendly and loves long walks."
          value={formValues.bio}
          onChange={handleChange}
          aria-invalid={Boolean(errors.bio)}
        />
        {errors.bio && <p className="text-sm text-destructive">{errors.bio}</p>}
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating profile...' : 'Create pet profile'}
      </Button>
      {submitMessage && <p className="text-sm text-muted-foreground">{submitMessage}</p>}
    </form>
  );
}
