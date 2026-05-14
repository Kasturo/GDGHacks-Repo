import { Link } from 'react-router-dom';
import { CreatePetForm } from '@/components/pets/CreatePetForm';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export function CreatePetPage() {
  return (
    <main className="mx-auto grid min-h-svh w-full place-items-center p-6">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl">Create your pet profile</CardTitle>
          <CardDescription>Add a pet to start swiping and matching.</CardDescription>
        </CardHeader>
        <CardContent>
          <CreatePetForm />
        </CardContent>
        <CardFooter>
          <Link to="/" className="text-sm text-primary underline-offset-4 hover:underline">
            Back to discover
          </Link>
        </CardFooter>
      </Card>
    </main>
  );
}
