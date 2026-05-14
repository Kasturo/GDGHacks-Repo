import { useCallback, useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const INITIAL_CARDS = [
  { id: 1, name: 'Milo', age: 3, bio: 'Loves beach walks and squeaky toys.' },
  { id: 2, name: 'Luna', age: 2, bio: 'Snack-motivated and nap-certified.' },
  { id: 3, name: 'Charlie', age: 4, bio: 'Professional tail wagger and hiker.' },
  { id: 4, name: 'Bella', age: 1, bio: 'Curious explorer who loves cuddles.' },
];

const SWIPE_THRESHOLD = 120;
const SWIPE_VELOCITY_THRESHOLD = 550;
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

const cardVariants = {
  initial: { scale: 0.95, opacity: 0, y: 20 },
  animate: { scale: 1, opacity: 1, y: 0 },
  exit: (direction) => ({
    opacity: 0,
    x: direction === 'right' ? 320 : -320,
    rotate: direction === 'right' ? 18 : -18,
    transition: { duration: 0.22 },
  }),
};

function getStoredAccessToken() {
  return localStorage.getItem('access_token') ?? '';
}

function getSwiperPetId() {
  const saved = localStorage.getItem('active_pet_id');
  const parsed = saved ? Number.parseInt(saved, 10) : Number.NaN;
  return Number.isFinite(parsed) ? parsed : null;
}

function mapPetToCard(pet) {
  return {
    id: pet.id,
    petId: pet.id,
    name: pet.name ?? 'Unknown',
    age: pet.age_years ?? '?',
    bio: pet.bio ?? 'No bio yet.',
    ownerId: pet.owner_id ?? null,
  };
}

export function MainPage() {
  const [cards, setCards] = useState(INITIAL_CARDS);
  const [lastAction, setLastAction] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [myPets, setMyPets] = useState([]);
  const [activePetId, setActivePetId] = useState(() => getSwiperPetId());
  const [swipeDirection, setSwipeDirection] = useState('right');

  const activeCard = useMemo(() => cards[cards.length - 1] ?? null, [cards]);

  const loadMyPets = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/pets/mine`, {
        headers: {
          Authorization: `Bearer ${getStoredAccessToken()}`,
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      const pets = Array.isArray(payload) ? payload : [];
      setMyPets(pets);

      if (!activePetId && pets.length > 0) {
        setActivePetId(pets[0].id);
        localStorage.setItem('active_pet_id', String(pets[0].id));
      } else if (pets.length === 0) {
        setActivePetId(null);
        localStorage.removeItem('active_pet_id');
      }
    } catch {
      setMyPets([]);
    }
  }, [activePetId]);

  const loadCards = useCallback(async () => {
    if (!activePetId) {
      setCards(INITIAL_CARDS);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/swipes/candidates?swiper_pet_id=${activePetId}`,
        {
          headers: {
            Authorization: `Bearer ${getStoredAccessToken()}`,
          },
        },
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      const petCards = Array.isArray(payload) ? payload.map(mapPetToCard) : [];
      setCards(petCards.length > 0 ? petCards : INITIAL_CARDS);
    } catch {
      // Keep development moving when backend pets endpoint is not ready yet.
      setCards(INITIAL_CARDS);
    } finally {
      setIsLoading(false);
    }
  }, [activePetId]);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadMyPets();
    }, 0);
    return () => clearTimeout(timer);
  }, [loadMyPets]);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadCards();
    }, 0);
    return () => clearTimeout(timer);
  }, [loadCards]);

  const handlePetChange = (event) => {
    const selectedId = Number.parseInt(event.target.value, 10);
    if (!Number.isFinite(selectedId)) {
      setActivePetId(null);
      localStorage.removeItem('active_pet_id');
      return;
    }
    setActivePetId(selectedId);
    localStorage.setItem('active_pet_id', String(selectedId));
  };

  /** Report swipe to the server without blocking UI (animations run immediately). */
  const submitSwipeToServer = useCallback(async (direction, cardSnapshot) => {
    if (!activePetId || !cardSnapshot) {
      return;
    }
    const swipedId = cardSnapshot.petId ?? cardSnapshot.id;

    if (direction === 'right') {
      const matchPayload = {
        swiper_pet_id: activePetId,
        swiped_pet_id: swipedId,
        direction: 'like',
      };
      try {
        const response = await fetch(`${API_BASE_URL}/api/swipes`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${getStoredAccessToken()}`,
          },
          body: JSON.stringify(matchPayload),
        });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const swipeResult = await response.json();
        setLastAction(
          swipeResult.is_match
            ? `It's a match with ${cardSnapshot.name}!`
            : `You liked ${cardSnapshot.name}. Waiting for a mutual like.`,
        );
      } catch {
        setLastAction(`Liked ${cardSnapshot.name}.`);
      }
    } else {
      const swipePayload = {
        swiper_pet_id: activePetId,
        swiped_pet_id: swipedId,
        direction: 'pass',
      };
      try {
        await fetch(`${API_BASE_URL}/api/swipes`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${getStoredAccessToken()}`,
          },
          body: JSON.stringify(swipePayload),
        });
      } catch {
        // Ignore until pass analytics or retry logic is needed.
      }
      setLastAction(`Passed on ${cardSnapshot.name}.`);
    }
  }, [activePetId]);

  const handleSwipe = (direction) => {
    if (!activeCard || !activePetId) {
      return;
    }

    const snapshot = activeCard;
    setSwipeDirection(direction);
    setCards((previous) => previous.slice(0, -1));
    void submitSwipeToServer(direction, snapshot);
  };

  const getSwipeDirection = (dragInfo) => {
    if (dragInfo.offset.x > SWIPE_THRESHOLD || dragInfo.velocity.x > SWIPE_VELOCITY_THRESHOLD) {
      return 'right';
    }
    if (dragInfo.offset.x < -SWIPE_THRESHOLD || dragInfo.velocity.x < -SWIPE_VELOCITY_THRESHOLD) {
      return 'left';
    }
    return null;
  };

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-2xl flex-col items-center justify-center gap-6 p-6">
      <h1 className="text-center text-4xl font-semibold tracking-tight">Discover</h1>
      <p className="text-sm text-muted-foreground">Swipe right to match, left to pass.</p>

      {!isLoading && myPets.length === 0 && (
        <section className="w-full max-w-lg rounded-xl border bg-card p-6 text-center shadow-sm">
          <h2 className="text-2xl font-semibold">Create your first pet profile</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            You need at least one pet profile before you can start swiping.
          </p>
          <div className="mt-4">
            <Button asChild>
              <Link to="/pets/create">Create pet profile</Link>
            </Button>
          </div>
        </section>
      )}

      {myPets.length > 0 && (
        <>
      <div className="w-full max-w-sm">
        <label htmlFor="active-pet" className="mb-1 block text-left text-sm text-muted-foreground">
          Active pet profile
        </label>
        <select
          id="active-pet"
          className="h-9 w-full rounded-md border bg-background px-3 text-sm"
          value={activePetId ?? ''}
          onChange={handlePetChange}
        >
          <option value="">Select a pet</option>
          {myPets.map((pet) => (
            <option key={pet.id} value={pet.id}>
              {pet.name} ({pet.species})
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading pets...</p>}

      <div className="relative h-112 w-full max-w-sm">
        <AnimatePresence custom={swipeDirection}>
          {cards.map((card, index) => {
            const isTopCard = index === cards.length - 1;
            return (
              <motion.article
                key={card.id}
                className="absolute inset-0 rounded-2xl border bg-card p-6 shadow-sm"
                style={{ zIndex: index }}
                custom={isTopCard ? swipeDirection : 'right'}
                variants={cardVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                drag={isTopCard ? 'x' : false}
                dragConstraints={{ left: -220, right: 220 }}
                dragElastic={0.75}
                onDragEnd={(_, info) => {
                  if (!isTopCard) {
                    return;
                  }
                  const direction = getSwipeDirection(info);
                  if (direction) {
                    handleSwipe(direction);
                  }
                }}
              >
                <div className="flex h-full flex-col justify-between">
                  <div className="space-y-2">
                    <h2 className="text-3xl font-semibold">{card.name}, {card.age}</h2>
                    <p className="text-sm text-muted-foreground">{card.bio}</p>
                  </div>
                  <div className="text-xs text-muted-foreground">Drag this card left or right</div>
                </div>
              </motion.article>
            );
          })}
        </AnimatePresence>
      </div>

      {!activeCard && (
        <Button type="button" variant="outline" onClick={loadCards}>
          Reload cards
        </Button>
      )}

      {lastAction && <p className="text-sm text-foreground">{lastAction}</p>}
        </>
      )}
    </main>
  );
}
